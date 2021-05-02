from logging import getLogger
import re
from typing import List
from itertools import product

logger = getLogger('squares')

tables_names = []
lines_names = {}
aggregate_functions = ['max', 'min', 'sum', 'count', 'avg']
attrs = []

class Child:
    def __init__(self, child: str = None, child_type: str = None) -> None:
        self.child = child
        self.productions = []
        self.type = None
        if child_type:
            self.check_type(child_type)
            self.var = None
        else:
            self.var = 0

    def get_name(self) -> str:
        return self.child

    def get_type(self) -> str:
        return self.type

    def check_type(self, child_type) -> None:
        self.type = child_type

        if child_type == "Table":
            for i in range(len(tables_names)):
                if tables_names[i] == self.child:
                    self.child = i
                    return

            for i in lines_names:
                if lines_names[i] == self.child:
                    self.child = i - 1
                    self.type = "Line"
                    return

            if self.child == "T??":     # TODO implement and test
                self.child = "??"
                self.type = "Line"
                return

        else:
            for column in columns_names:
                if column in self.child and column not in attrs:
                    attrs.append(column)

            if child_type == "FilterCondition" or child_type == "CrossJoinCondition":
                self.productions = redundant_boolean_conditions(self.child)

            else:
                if child_type == "Cols" or child_type == "JoinCondition":
                    if self.child != '':
                        self.child = add_quotes(self.child)
                self.productions = redundant_conditions(self.child)

    def __repr__(self) -> str:
        return f'Child({self.child}, type={self.type}, var={self.var})'


class Line:
    def __init__(self, line_id: float = None, name: str = None, root: str = None, children: List[Child] = None, n_children: int = None) -> None:
        self.name = name
        self.root = root
        self.children = children
        self.n_children = n_children
        self.var = None
        if name and line_id != float('inf'):
            lines_names[line_id] = name

    def get_root(self) -> str:
        return self.root

    def get_n_children(self) -> int:
        return self.n_children

    def get_child(self, n) -> Child:
        return self.children[n]

    def add_child(self, child) -> None:
        self.children.append(child)

    def __repr__(self) -> str:
        string = f'Line({self.name}, root={self.root}, var={self.var}, children=['
        for c in self.children:
            string += str(c) + ","
        string += "])"
        return string


######## AUXILIARY PARSE FUNCTIONS ########

def args_in_brackets(string: str):
    brackets = 0
    start = 0
    matches = []
    string = string.partition("(")[2]
    string = string.rpartition(")")[0]
    string = string.strip()

    for i in range(len(string)):
        if string[i] == '(':
            brackets += 1
        elif string[i] == ')':
            brackets -= 1
        elif string[i] == "," and not brackets:
            match = string[start:i].strip()
            if match[0] == "(" and match[-1] == ")":
                match = match[1:-1].strip()
            matches.append(match)
            start = i + 1

    if brackets != 0:
        return None

    match = string[start:len(string)].strip()
    if match and match[0] == "(" and match[-1] == ")":
        match = match[1:-1].strip()
    matches.append(match)

    return matches

def check_underscore_args(function: str, arg: str) -> str:
    variations = ["all", "at", "if"]
    var = function.partition("_")[2]

    if var in variations:
        arg = var + "$" + arg

    return arg

def add_quotes(string: str) -> str:
    new_string = ""

    string = string.replace(" ", "").replace("'", "").split(",")
    for s in string:
        if "=" in s:
            new = s.split("=")
            new_string += "'" + new[0] + "'" + " = " + "'" + new[1] + "'" + ","
        else:
            new_string += "'" + s + "'" + ","
    new_string = new_string[:-1]

    return new_string

def redundant_conditions(condition: str) -> List[str]:
    conditions = []
    final = []

    if "," in condition:
        conditions = condition.split(",")

    if len(conditions) > 1:
        final.append(str(conditions[0].strip() + "," + conditions[1].strip()))
        final.append(str(conditions[1].strip() + "," + conditions[0].strip()))

    else:
        if "=" in condition:
            parts = condition.split("=")
            final.append(str(parts[0].strip() + " = " + parts[1].strip()))
            final.append(str(parts[1].strip() + " = " + parts[0].strip()))
        else:
            final.append(condition)

    return final

def redundant_boolean_conditions(condition: str) -> List[str]:
    separators = ["|", "&"]
    comparators = ["==", "!=", "<=", ">=", "<", ">"]
    final = []
    conditions = []
    productions = []
    condition = condition.replace("=>", ">=").replace("=<", "<=")

    for separator in separators:
        if separator in condition:
            conditions = condition.split(separator)
            break

    if not conditions:
        conditions.append(condition)

    for condition in conditions:
        production_part = []
        condition = condition.strip()
        for comparator in comparators:
            parts = condition.split(comparator)
            if comparator in condition:
                production_part.append(str(parts[0].strip()) + " " + str(comparator) + " " + str(parts[1].strip()))
                if comparator == ">":
                    comparator = "<="
                elif comparator == "<":
                    comparator = ">="
                elif comparator == "<=":
                    comparator = ">"
                elif comparator == ">=":
                    comparator = "<"
                production_part.append(str(parts[1].strip()) + " " + str(comparator) + " " + str(parts[0].strip()))
                productions.append(production_part)
                break

    if len(productions) > 1:
        combinations = list(product(*productions))
        for combination in combinations:
            final.append(str(combination[0]) + " " + separator + " " + str(combination[1]))
            final.append(str(combination[1]) + " " + separator + " " + str(combination[0]))
    else:
        final = productions[0]

    return final


class Sketch:

    def __init__(self, sketch) -> None:
        self.sketch = sketch
        self.lines = sketch.splitlines()
        self.loc = len(self.lines) - 1
        self.min_loc = 0
        self.max_loc = 0
        self.lines_encoding = {}
        self.free_children = []
        self.free_lines = []
        self.aggrs = []

    def sketch_parser(self, tables: List[str], columns: List[str]) -> None:
        # TODO verificar os types
        # TODO if none function - ??
        logger.info("Parsing sketch...")

        for table in tables:
            table = table.split(".")[0].split("/")[-1]
            tables_names.append(table)

        global columns_names
        columns_names = columns
        parsed = True

        for sketch_line in self.lines:

            if sketch_line.startswith("out"):
                pass # TODO parse Select

            elif sketch_line.startswith("child"):
                pass # TODO implement child we don't know the place

            elif sketch_line.startswith("??"):
                # TODO implement in bitenum
                line = sketch_line.strip()
                if line == "??+":
                    self.max_loc = float('inf')
                    self.min_loc += 1

                elif line == "??*":
                    self.max_loc = float('inf')

                else:
                    logger.error('Sketch line "%s" could not be parsed', sketch_line)
                    parsed = False
                    break
            else:
                self.min_loc += 1
                self.max_loc += 1
                line = sketch_line.partition("=")
                name = line[0].replace(" ", "")
                args = args_in_brackets(line[2].strip())
                line = line[2].partition("(")
                function = line[0].replace(" ", "")

                if not args:
                    logger.error('Sketch line "%s" has missing brackets', sketch_line)
                    parsed = False
                    break

                children = []
                n_children = 0

                # TODO SELECT statement
                try:
                    if "??" == function:
                        # A line with no function. Can have children or not
                        if self.max_loc != float('inf'):
                            lines_names[self.max_loc] = name

                        if args[0]:
                            self.min_loc -= 1
                            self.max_loc -= 1
                            args = args_in_brackets(sketch_line)
                            for arg in args:
                                self.free_children.append(Child(arg))  # TODO parse do arg para ter aspas e todas as redundancias

                            # TODO parse free children and children that we know were they are. we can also roughly know the place in cases of ??*+

                    elif "natural_join" == function:
                        n_children = 2
                        if len(args) > 4:
                            logger.error('Can only support Natural Join up to 4 tables')
                            parsed = False
                            break
                        else:
                            for arg in args:
                                children.append(Child(arg, "Table"))

                            if len(children) > 2:
                                n_children = len(children)
                                function += str(len(children))

                    elif "inner_join" == function:  # Build error function if args != from the right #
                        n_children = 3
                        children.append(Child(args[0], "Table"))
                        children.append(Child(args[1], "Table"))
                        children.append(Child(args[2], "JoinCondition"))

                    elif "anti_join" == function:
                        n_children = 3
                        children.append(Child(args[0], "Table"))
                        children.append(Child(args[1], "Table"))
                        if len(args) > 2:
                            children.append(Child(args[2], "Cols"))
                        else:
                            children.append(Child('', "Cols"))

                    elif "left_join" == function or "union" == function or "semi_join" == function:
                        n_children = 2
                        children.append(Child(args[0], "Table"))
                        children.append(Child(args[1], "Table"))

                    elif "intersect" == function:   # TODO test
                        n_children = 3
                        children.append(Child(args[0], "Table"))
                        children.append(Child(args[1], "Table"))
                        children.append(Child(args[2], "Col"))

                    elif "cross_join" == function:
                        n_children = 3
                        children.append(Child(args[0], "Table"))
                        children.append(Child(args[1], "Table"))
                        children.append(Child(args[2], "CrossJoinCondition"))

                    elif "unite" == function:
                        n_children = 3
                        children.append(Child(args[0], "Table"))
                        children.append(Child(args[1], "Col"))
                        children.append(Child(args[2], "Col"))

                    elif "filter" == function:
                        n_children = 2
                        children.append(Child(args[0], "Table"))
                        children.append(Child(args[1], "FilterCondition"))

                    elif "summarise" in function:
                        n_children = 3
                        arg = check_underscore_args(function, args[1])
                        function = "summarise"

                        children.append(Child(args[0], "Table"))
                        children.append(Child(arg, "SummariseCondition"))

                        for aggr in aggregate_functions:        #TODO check if table is called max/min something
                            if aggr in arg:
                                self.aggrs.append(aggr)

                        if len(args) > 2:
                            children.append(Child(args[2], "Cols"))
                        else:
                            children.append(Child('', "Cols"))

                    elif "mutate" in function:
                        n_children = 2
                        arg = check_underscore_args(function, args[1])
                        function = "mutate"

                        children.append(Child(args[0], "Table"))
                        children.append(Child(arg, "SummariseCondition"))

                        for aggr in aggregate_functions:        #TODO check if table is called max/min something
                            if aggr in arg:
                                self.aggrs.append(aggr)

                    else:   # TODO something similar for children
                        logger.error('Sketch line "%s" could not be parsed', sketch_line)
                        parsed = False
                        break

                except IndexError:
                    logger.error('Sketch line "%s" has not enough arguments', sketch_line)
                    parsed = False
                    break

                if n_children < len(args) and parsed:
                    logger.error('Sketch line "%s" has too many arguments', sketch_line)
                    parsed = False
                    break

                line = Line(self.max_loc, name, function, children, n_children)
                if self.max_loc != float('inf'):
                    self.lines_encoding[self.max_loc] = line
                else:
                    self.free_lines.append(line)

                logger.debug("Sketch creation: " + str(line))

        if not parsed:
            raise RuntimeError("Could not parse sketch")

    def get_aggrs(self) -> List[str]:
        return self.aggrs

    def get_attrs(self) -> List[str]:
        return attrs

    def fill_vars(self, spec, line_productions) -> None:
        # TODO have to check if there's root and children
        for line in self.lines_encoding.values():
            prod_name = line.get_root()
            prod = spec.get_function_production(prod_name)

            if prod:
                line.var = prod.id
            else:
                logger.error('Unknown function production "%s"', prod_name)
                raise RuntimeError("Could not process sketch function")

            n_children = line.get_n_children()

            for c in range(spec.max_rhs):  # TODO check when we don't know which function

                if c < n_children:

                    child = line.get_child(c)
                    prod_type = child.get_type()
                    prod_name = child.get_name()

                    if prod_name != "??":
                        if prod_type == "Table":
                            prod = spec.get_param_production(prod_name)
                            if prod:
                                child.var = prod.id
                            else:
                                logger.warning('Unknown Table production "%s"', prod_name)
                        elif prod_type == "Line":
                            prod = line_productions[prod_name][0]       # check type if not more line prods
                            if prod:
                                child.var = prod.id
                            else:
                                logger.warning('Unknown Line production "%s"', prod_name)
                        else:
                            prod_type = spec.get_type(prod_type)
                            for name in child.productions:
                                prod = spec.get_enum_production(prod_type, name)
                                if prod:
                                    child.var = prod.id
                                    break

                            if not prod:
                                logger.warning('Unknown %s production "%s"', prod_type, prod_name)

                else:
                    child = Child()
                    child.var = 0
                    line.add_child(child)

        logger.debug(self.lines_encoding)