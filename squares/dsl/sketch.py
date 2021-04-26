from logging import getLogger
import re
from typing import List

logger = getLogger('squares')

tables_names = []
lines_names = []
aggregate_functions = ['max', 'min', 'sum', 'count', 'avg']
attrs = []

class Child:
    def __init__(self, child_type: str = None, child: str = None) -> None:
        self.child = child
        self.type = None
        if child_type is not None and child is not None:
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

            for i in range(len(lines_names)):
                if lines_names[i] == self.child:
                    self.child = i
                    self.type = "Line"
                    return

        else:
            for column in columns_names:
                if column in self.child and column not in attrs:
                    attrs.append(column)

    def __repr__(self) -> str:
        return f'Child({self.child}, type={self.type}, var={self.var})'


class Line:
    def __init__(self, name: str = None, root: str = None, children: List[Child] = None, n_children: int = None) -> None:
        self.name = name
        self.root = root
        self.children = children
        self.n_children = n_children
        self.var = None
        if self.name is not None:
            lines_names.append(name)

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

def args_in_brackets(string: str) -> List[str]:
    brackets = 0
    start = 0
    matches = []
    string = string.strip()
    string = string.rpartition(")")[0]

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

    match = string[start:len(string)].strip()
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

    if string:
        string = string.replace(" ", "").split(",")
        for s in string:
            if "=" in s:
                new = s.split("=")
                new_string += "'" + new[0] + "'" + " = " + "'" + new[1] + "'" + ","
            else:
                new_string += "'" + s + "'" + ","
        new_string = new_string[:-1]

    return new_string


class Sketch:

    def __init__(self, sketch) -> None:
        self.sketch = sketch
        self.lines = sketch.splitlines()
        self.loc = len(self.lines) - 1
        self.lines_encoding = []
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

        for sketch_line in self.lines[:-1]: # TODO parse last line
            parsed = True
            line = sketch_line.partition("=")
            name = line[0].replace(" ", "")
            line = line[2].partition("(")
            function = line[0].replace(" ", "")
            args = args_in_brackets(line[2])
            children = []
            n_children = 0

            # TODO SELECT statement
            try:
                if "natural_join" == function:
                    n_children = 2
                    if len(args) > 4:
                        logger.error('Can only support Natural Join up to 4 tables')
                        parsed = False
                    else:
                        for arg in args:
                            children.append(Child("Table", arg))

                        if len(children) > 2:
                            n_children = len(children)
                            function += str(len(children))

                elif "inner_join" == function:  # Build error function if args != from the right #
                    n_children = 3
                    children.append(Child("Table", args[0]))
                    children.append(Child("Table", args[1]))
                    arg = add_quotes(args[2])
                    children.append(Child("JoinCondition", arg))

                elif "anti_join" == function:
                    n_children = 3
                    children.append(Child("Table", args[0]))
                    children.append(Child("Table", args[1]))
                    if len(args) > 2:
                        arg = add_quotes(args[2])
                    else:
                        arg = ''
                    children.append(Child("Cols", arg))

                elif "left_join" == function or "union" == function or "semi_join" == function:
                    n_children = 2
                    children.append(Child("Table", args[0]))
                    children.append(Child("Table", args[1]))

                elif "intersect" == function:   # TODO test
                    n_children = 3
                    children.append(Child("Table", args[0]))
                    children.append(Child("Table", args[1]))
                    children.append(Child("Col", args[2]))

                elif "cross_join" == function:
                    n_children = 3
                    children.append(Child("Table", args[0]))
                    children.append(Child("Table", args[1]))
                    children.append(Child("CrossJoinCondition", args[2]))

                elif "unite" == function:
                    n_children = 3
                    children.append(Child("Table", args[0]))
                    children.append(Child("Col", args[1]))
                    children.append(Child("Col", args[2]))

                elif "filter" == function:
                    n_children = 2
                    children.append(Child("Table", args[0]))
                    children.append(Child("FilterCondition", args[1]))

                elif "summarise" in function:
                    n_children = 3
                    arg = check_underscore_args(function, args[1])
                    function = "summarise"

                    children.append(Child("Table", args[0]))
                    children.append(Child("SummariseCondition", arg))

                    for aggr in aggregate_functions:        #TODO check if table is called max/min something
                        if aggr in arg:
                            self.aggrs.append(aggr)

                    if len(args) > 2:
                        arg = add_quotes(args[2])
                    else:
                        arg = ''
                    children.append(Child("Cols", arg))

                elif "mutate" in function:
                    n_children = 2
                    arg = check_underscore_args(function, args[1])
                    function = "mutate"

                    children.append(Child("Table", args[0]))
                    children.append(Child("SummariseCondition", arg))

                    for aggr in aggregate_functions:        #TODO check if table is called max/min something
                        if aggr in arg:
                            self.aggrs.append(aggr)

                else:   # TODO something similar for children
                    function = None
                    name = None
                    logger.warning('Sketch line "%s" could not be completely parsed', sketch_line)

            except IndexError:
                logger.error('Sketch line "%s" has not enough arguments', sketch_line)
                parsed = False

            if n_children < len(args) and parsed:
                logger.error('Sketch line "%s" has too many arguments', sketch_line)
                parsed = False

            if not parsed:
                raise RuntimeError("Could not parse sketch")

            self.lines_encoding.append(Line(name, function, children, n_children))
            logger.debug("Sketch creation: " + str(self.lines_encoding[-1]))

    def get_aggrs(self) -> List[str]:
        return self.aggrs

    def get_attrs(self) -> List[str]:
        return attrs

    def fill_vars(self, spec, line_productions) -> None:
        # TODO have to check if there's root and children
        for line in self.lines_encoding:       # It assumes the lines in sketch are exact
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
                            prod = spec.get_enum_production(spec.get_type(prod_type), prod_name)
                            if prod:
                               child.var = prod.id
                            else:
                                logger.warning('Unknown %s production "%s"', prod_type, prod_name)

                else:
                    child = Child()
                    child.var = 0
                    line.add_child(child)

        logger.debug(self.lines_encoding)