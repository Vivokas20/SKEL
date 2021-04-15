import io
import os
import re
from collections import defaultdict
from functools import reduce
from logging import getLogger
from typing import Dict, Sequence, Any

import operator
import pandas
from ordered_set import OrderedSet
from pandas import DataFrame
from rpy2 import robjects
# from rpy2.rinterface_lib.embedded import RRuntimeError

from . import dsl
from .conditions import ConditionGenerator
from .. import util, types
from ..exceptions import SquaresException
from ..tyrell.spec import TyrellSpec, TypeSpec, ProductionSpec, ProgramSpec, ValueType
from ..tyrell.spec.spec import PredicateSpec
from ..util import powerset_except_empty
from .sketch import Sketch

logger = getLogger('squares')


def exec_and_return(r_script: str) -> str:
    # print(r_script)
    robjects.r(r_script)
    return r_script


def add_is_not_parent_if_enabled(pred_spec: PredicateSpec, a: Any, b: Any) -> None:
    if a not in util.get_config().disabled and b not in util.get_config().disabled:
        pred_spec.add_predicate('is_not_parent', [a, b])


class Specification:

    def __init__(self, spec) -> None:
        self.inputs = spec['inputs']
        self.output = spec['output']
        self.consts = spec['constants'] or []

        if util.get_config().ignore_aggrs:
            self.aggrs = util.get_config().aggregation_functions
        else:
            self.aggrs = spec['functions'] or []

        self.attrs = spec['columns'] or []
        self.dateorder = spec['dateorder'] or 'parse_datetime'
        self.filters = spec['filters'] or []

        if 'solution' in spec:
            self.solution = spec['solution']
        else:
            self.solution = None

        if util.get_config().use_solution_dsl and self.solution:
            util.get_config().disabled = OrderedSet(util.get_config().disabled) | (dsl.functions - OrderedSet(self.solution))

        self.aggrs_use_const = False

        self.tables = []
        self.data_frames = {}

        self.columns = OrderedSet()
        self.column_replacements = defaultdict(dict)
        self.generated_columns = {}
        self.columns_by_type = types.empty_type_map()
        self.types_by_const = {}
        self.consts_by_type = types.empty_type_map()

        if 'max(n)' in self.aggrs:
            raise SquaresException('max(n) is not a valid aggregator. Use a filter instead.')

        if spec['sketch']:
            self.sketch = Sketch(spec['sketch'])
            self.sketch.sketch_parser(self.inputs)
            self.min_loc = self.sketch.loc  # TODO fazer mais hard lock e tirar o while
        else:
            self.sketch = None
            self.min_loc = max((len(self.aggrs) if util.get_config().force_summarise else 0) + (
                1 if self.filters or self.consts else 0),
                               util.get_config().minimum_loc)  # TODO change for loc to be fixed

        logger.debug("Reading input files...")
        for input in self.inputs:
            table_name = 'df_' + os.path.splitext(os.path.basename(input))[0]
            table_name = re.sub('[^a-zA-Z0-9._]', '_', table_name)
            self.tables.append(table_name)
            df = self.read_table(input, table_name)

            for column, type in df.dtypes.items():
                type = types.get_type(type)
                self.columns_by_type[type].add(column)

            self.data_frames[table_name] = df
            self.columns |= df.columns
        self.columns = OrderedSet(sorted(self.columns))
        self.all_columns = self.columns.copy()

        self.data_frames['expected_output'] = self.read_table(self.output, 'expected_output')
        self.output_cols = self.data_frames['expected_output'].columns

        for const in self.consts:
            self.types_by_const[const] = []

            for type in types.Type:
                if types.is_type(const, type):
                    self.types_by_const[const].append(type)
                    self.consts_by_type[type].append(const)

        self.condition_generator = ConditionGenerator(self)
        self.condition_generator.generate()

        self.n_columns = len(self.all_columns)

        self.generate_r_init()

        self.tyrell_spec = None

    def read_table(self, path: str, table_name:str = None) -> DataFrame:
        df = pandas.read_csv(path)
        df = df.convert_dtypes(convert_integer=False, convert_boolean=False)

        replacements = {}

        for col in df.columns:
            new_col, n = re.subn('[^a-zA-Z0-9_]', '_', col)
            new_col, n2 = re.subn('^([0-9_])', r'col_\1', new_col)
            if n + n2:
                logger.warning('Column names should be valid R identifiers. Trying to fix names. Conflicts may arise!')
                logger.warning('Replacing column "%s" in table %s with %s', col, path, new_col)
                replacements[col] = new_col

        if replacements and table_name:
            self.column_replacements[table_name] = replacements.copy()

        df = df.rename(columns=replacements)

        for col in df:  # try to coerce columns to datetime
            if types.get_type(df[col].dtype) == types.INT:
                for elem in df[col]:
                    if elem >= 2 ** 32 - 1:
                        logger.warning('Using integers larger than 32 bits! Converting column %s to string.', col)
                        df[col] = df[col].astype(str)
                        break

            if all(types.is_time(elem) or pandas.isna(elem) for elem in df[col]) and any(types.is_time(elem) for elem in df[col]):
                try:
                    df[col] = pandas.to_timedelta(df[col], errors='coerce')
                except Exception:
                    pass

            elif all(types.is_date(elem) or pandas.isna(elem) for elem in df[col]) and any(types.is_date(elem) for elem in df[col]):
                try:
                    df[col] = pandas.to_datetime(df[col], errors='coerce')
                except Exception:
                    pass

        logger.info('Inferred data types for table %s: %s', path, str(list(map(str, df.dtypes.values))))
        return df

    def generate_r_init(self) -> None:  # TODO dirty: initializes R for the inputs
        self.r_init = 'con <- DBI::dbConnect(RSQLite::SQLite(), ":memory:")\n'

        for table, file in zip(self.tables, self.inputs):
            df = self.data_frames[table]
            self.r_init += exec_and_return(f'{table} <- read_csv("{file}", col_types = cols({types.get_r_types(df.dtypes, self.column_replacements[table])}))\n')

            if table in self.column_replacements:
                for old, new in self.column_replacements[table].items():
                    self.r_init += exec_and_return(f'{table} <- rename({table}, {new} = "{old}")\n')

            for col, dtype in zip(df.columns, df.dtypes):  # parse dates
                if types.get_type(dtype) == types.DATETIME:
                    self.r_init += exec_and_return(f'{table}${col} <- {self.dateorder}({table}${col})\n')

            self.r_init += f'{table} <- copy_to(con, {table})\n'

        output_df = self.data_frames['expected_output']
        self.r_init += exec_and_return(
            f'expected_output <- read_csv("{self.output}", col_types = cols({types.get_r_types(output_df.dtypes, self.column_replacements["expected_output"])}))\n')
        if 'expected_output' in self.column_replacements:
            for old, new in self.column_replacements['expected_output'].items():
                self.r_init += exec_and_return(f'expected_output <- rename(expected_output, {new} = "{old}")\n')
        for col, dtype in zip(output_df.columns, output_df.dtypes):  # parse dates
            if types.get_type(dtype) == types.DATETIME:
                self.r_init += exec_and_return(f'expected_output${col} <- {self.dateorder}(expected_output${col})\n')

        if 'concat' in self.aggrs:
            self.r_init += exec_and_return('\nstring_agg <- function(v,s) {paste0("", Reduce(function(x, y) paste(x, y, sep = s), v))}\n')
        if 'mode' in self.aggrs:
            self.r_init += exec_and_return('\nmode <- function(x) {ux <- unique(x); ux[which.max(tabulate(match(x, ux)))]}\n')

    def generate_dsl(self, discard: bool = False) -> TyrellSpec:
        if self.tyrell_spec and not discard:
            return self.tyrell_spec

        type_spec = TypeSpec()

        Empty = ValueType('Empty')
        type_spec.define_type(Empty)

        type_spec.define_type(dsl.Table)

        if 'intersect' not in util.get_config().disabled:
            dsl.Col.set_domain([(column, self.get_bitvecnum([column])) for column in self.columns])
            type_spec.define_type(dsl.Col)

        if 'anti_join' not in util.get_config().disabled or self.condition_generator.summarise_conditions:
            dsl.Cols.set_domain([('', 0)] + [(','.join(map(util.single_quote_str, cols)), self.get_bitvecnum(cols)) for cols in
                                                 powerset_except_empty(self.columns, util.get_config().max_column_combinations)])
            type_spec.define_type(dsl.Cols)

        if 'inner_join' not in util.get_config().disabled and self.condition_generator.inner_join_conditions:
            dsl.JoinCondition.set_domain(self.condition_generator.inner_join_conditions)
            type_spec.define_type(dsl.JoinCondition)

        if 'cross_join' not in util.get_config().disabled and self.condition_generator.cross_join_conditions:
            dsl.CrossJoinCondition.set_domain(self.condition_generator.cross_join_conditions)
            type_spec.define_type(dsl.CrossJoinCondition)

        if self.condition_generator.filter_conditions:
            dsl.FilterCondition.set_domain(self.condition_generator.filter_conditions)
            type_spec.define_type(dsl.FilterCondition)

        if self.condition_generator.summarise_conditions:
            dsl.SummariseCondition.set_domain(self.condition_generator.summarise_conditions)
            type_spec.define_type(dsl.SummariseCondition)

        if util.get_config().filters_function_enabled and len(self.condition_generator.filter_conditions) > 1:
            dsl.Op.set_domain(['|', '&'])
            type_spec.define_type(dsl.Op)

        prod_spec = ProductionSpec()

        prod_spec.add_func_production('empty', Empty, [Empty])

        if 'natural_join' not in util.get_config().disabled:
            prod_spec.add_func_production(*dsl.natural_join)

        if 'natural_join3' not in util.get_config().disabled:
            prod_spec.add_func_production(*dsl.natural_join3)

        if 'natural_join4' not in util.get_config().disabled:
            prod_spec.add_func_production(*dsl.natural_join4)

        if 'inner_join' not in util.get_config().disabled and self.condition_generator.inner_join_conditions:
            prod_spec.add_func_production(*dsl.inner_join)

        if 'anti_join' not in util.get_config().disabled:
            prod_spec.add_func_production(*dsl.anti_join)

        if 'left_join' not in util.get_config().disabled:
            prod_spec.add_func_production(*dsl.left_join)

        if 'union' not in util.get_config().disabled:
            prod_spec.add_func_production(*dsl.union)

        if 'intersect' not in util.get_config().disabled:
            prod_spec.add_func_production(*dsl.intersect)

        if 'semi_join' not in util.get_config().disabled:
            prod_spec.add_func_production(*dsl.semi_join)

        if 'cross_join' not in util.get_config().disabled:
            prod_spec.add_func_production(*dsl.cross_join)

        if 'concat' in self.aggrs:
            prod_spec.add_func_production(*dsl.unite)

        if self.condition_generator.filter_conditions:
            prod_spec.add_func_production(*dsl.filter)

            if util.get_config().filters_function_enabled and len(self.condition_generator.filter_conditions) > 1:
                prod_spec.add_func_production(*dsl.filters)

        if self.condition_generator.summarise_conditions and 'summarise' not in util.get_config().disabled:
            prod_spec.add_func_production(*dsl.summarise)

        if self.condition_generator.summarise_conditions and 'mutate' not in util.get_config().disabled:
            prod_spec.add_func_production(*dsl.mutate)

        pred_spec = PredicateSpec()

        # if self.condition_generator.summarise_conditions and 'summarise' not in util.get_config().disabled:
        #     pred_spec.add_predicate('is_not_parent', ['summarise', 'summarise'])

        if len(self.condition_generator.filter_conditions) >= 1:
            # add_is_not_parent_if_enabled(pred_spec, 'filter', 'inner_join')
            # add_is_not_parent_if_enabled(pred_spec, 'filter', 'natural_join')
            # add_is_not_parent_if_enabled(pred_spec, 'filter', 'natural_join3')
            # add_is_not_parent_if_enabled(pred_spec, 'filter', 'natural_join4')
            # add_is_not_parent_if_enabled(pred_spec, 'inner_join', 'filter')
            # add_is_not_parent_if_enabled(pred_spec, 'natural_join', 'filter')
            # add_is_not_parent_if_enabled(pred_spec, 'natural_join3', 'filter')
            # add_is_not_parent_if_enabled(pred_spec, 'natural_join4', 'filter')
            pass
        elif len(self.condition_generator.filter_conditions) > 1 and util.get_config().filters_function_enabled:
            pred_spec.add_predicate('distinct_filters', ['filters', 1, 2])
            pred_spec.add_predicate('is_not_parent', ['filters', 'filter'])
            # pred_spec.add_predicate('is_not_parent', ['filter', 'filters'])
            pred_spec.add_predicate('is_not_parent', ['filter', 'filter'])
            # pred_spec.add_predicate('is_not_parent', ['filters', 'filters'])

        for p in self.condition_generator.predicates:
            pred_spec.add_predicate(*p)

        add_is_not_parent_if_enabled(pred_spec, 'natural_join', 'natural_join')
        add_is_not_parent_if_enabled(pred_spec, 'natural_join', 'natural_join3')
        add_is_not_parent_if_enabled(pred_spec, 'natural_join', 'natural_join4')
        add_is_not_parent_if_enabled(pred_spec, 'natural_join3', 'natural_join')
        add_is_not_parent_if_enabled(pred_spec, 'natural_join3', 'natural_join4')
        add_is_not_parent_if_enabled(pred_spec, 'anti_join', 'anti_join')
        add_is_not_parent_if_enabled(pred_spec, 'anti_join', 'natural_join')
        add_is_not_parent_if_enabled(pred_spec, 'anti_join', 'natural_join3')
        add_is_not_parent_if_enabled(pred_spec, 'anti_join', 'natural_join4')

        for join in ['natural_join4', 'natural_join3', 'natural_join', 'anti_join', 'semi_join', 'left_join']:
            if join not in util.get_config().disabled:
                pred_spec.add_predicate('distinct_inputs', [join])

        program_spec = ProgramSpec('squares', [(dsl.Table, self.get_bitvecnum(self.data_frames[input])) for input in self.tables],
                                   (dsl.Table, self.get_bitvecnum(self.data_frames["expected_output"])))

        self.tyrell_spec = TyrellSpec(type_spec, program_spec, prod_spec, pred_spec)
        function_difficulty = {prod.name: reduce(operator.mul, (len(rhs.domain) if rhs.is_enum() else len(self.inputs) for rhs in prod.rhs), 1) for prod
                  in self.tyrell_spec.get_function_productions() if prod.name != 'empty'}
        logger.debug(function_difficulty)
        function_difficulty = {key: value / sum( function_difficulty.values()) for key, value in function_difficulty.items()}
        logger.debug(function_difficulty)
        function_difficulty = {key: value / sum(function_difficulty.values()) for key, value in
                               function_difficulty.items()}
        logger.debug(function_difficulty)

        return self.tyrell_spec

    def get_bitvecnum(self, columns: Sequence[str]) -> int:
        return util.boolvec2int([column in columns for column in self.all_columns])

    def filter_columns(self, columns_map: Dict[types.Type, OrderedSet[str]]) -> Dict[types.Type, OrderedSet[str]]:
        d = {}
        for type in columns_map.keys():
            d[type] = OrderedSet()
            for column in columns_map[type]:
                if column in self.attrs or util.get_config().ignore_attrs or column in self.generated_columns.keys():
                    d[type].add(column)
        return d

    def constant_occurs(self, column: str, constant: str) -> bool:
        for data_frame in self.data_frames.values():
            if column in data_frame.columns:
                if constant is None:
                    if any(pandas.isna(data_frame[column])):
                        return True
                else:
                    if constant in data_frame[column].dropna().values:
                        return True
        return False

    def __str__(self) -> str:
        buffer = io.StringIO()
        buffer.write(repr(self.generate_dsl()))
        # buffer.write('\nMore restrictive:\n')
        # for type in self.condition_generator.more_restrictive.graphs.keys():
        #     max_length = max(map(len, self.condition_generator.more_restrictive.graphs[type])) + 1
        #     buffer.write(f'\t{type}:\n')
        #     for key in list(self.condition_generator.more_restrictive.graphs[type]):
        #         buffer.write(f'\t\t{key.ljust(max_length)}: {self.condition_generator.more_restrictive.dfs(type, key).items}\n')
        # buffer.write('Less restrictive:\n')
        # for type in self.condition_generator.less_restrictive.graphs.keys():
        #     max_length = max(map(len, self.condition_generator.less_restrictive.graphs[type])) + 1
        #     buffer.write(f'\t{type}:\n')
        #     for key in list(self.condition_generator.less_restrictive.graphs[type]):
        #         buffer.write(f'\t\t{key.ljust(max_length)}: {self.condition_generator.less_restrictive.dfs(type, key).items}\n')
        return buffer.getvalue()
