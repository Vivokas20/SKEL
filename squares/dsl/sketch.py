from logging import getLogger
import re
from squares import util
from typing import List
from itertools import product

logger = getLogger('squares')

######## FLAGS ########
flag_types = True

tables_names = []
lines_names = {}
columns_names = []
aggregate_functions = ['max', 'min', 'sum', 'count', 'avg']
attrs = []

######## AUXILIARY SKETCH CLASSES ########

class Child:
    def __init__(self, child = None, child_type: str = None, real_name = None) -> None:
        self.real_name = real_name
        if isinstance(child, list):
            self.names = child
        else:
            self.names = [child]
        self.productions = []
        self.type = None
        self.list_vars = []
        self.var = []
        self.line = False
        if child_type:
            self.check_type(child_type) # Ver se len > 1?

    def check_type(self, child_type) -> None:
        for n in range(len(self.names)):
            name = self.names[n]

            if child_type == "Unknown" and name != "??":    # Table
                if name in tables_names or name in lines_names.values() or "T??" in name:
                    child_type = "Table"

                else:
                    comparators = ["==", "!=", "<=", ">=", "<", ">"]
                    for comparator in comparators:
                        if comparator in name:  # CrossJoin or Filter
                            self.productions.append(redundant_boolean_conditions(name))
                            break
                    if not self.productions:    # Col, Cols, JoinCond, SummariseCond
                        self.productions.append(redundant_conditions(name))

            self.type = child_type

            if child_type == "Table" and name != "??":
                if name == "T??":     # TODO implement and test
                    self.names[n] = "??"
                    self.type = "Line"
                    return

                for i in range(len(tables_names)):
                    if tables_names[i] == name:
                        self.names[n] = i
                        return

                for i in lines_names:
                    if lines_names[i] == name:
                        self.names[n] = i - 1
                        self.type = "Line"
                        return

            elif child_type != "Unknown" and name != '??':

                if child_type == "FilterCondition" or child_type == "CrossJoinCondition":
                    self.productions.append(redundant_boolean_conditions(name))

                else:
                    self.productions.append(redundant_conditions(self.names[n]))

    def __repr__(self) -> str:
        return f'Child({self.names}, type={self.type}, var={self.var})'

    # def __repr__(self) -> str:
    #     return f'Child({self.real_name}, {self.type})'


class Line:
    def __init__(self, line_id: float = None, name: str = None, root: str = None, children: List[Child] = None, n_children: int = None, line_type: str = None, real_function: str = None) -> None:
        self.name = name
        self.real_root = real_function
        self.options = False
        if isinstance(root, list):
            self.root = root
            self.options = True
        else:
            self.root = [root]
        self.children = children
        self.n_children = n_children
        self.children_types = []
        if children:
            for c in children:
                if c.type and c.type != "Unknown":
                    if c.type == "Line":
                        t = "Table"
                    else:
                        t = c.type
                    self.children_types.append(t)
        self.line_type = line_type
        self.var = []
        if name and line_id != float('inf'):
            lines_names[line_id] = name     # TODO add name even if we don't know position

    def get_child(self, n) -> Child:
        return self.children[n]

    def add_child(self, child) -> None:
        self.children.append(child)

    def __repr__(self) -> str:
        string = f'Line({self.name}, root={self.root}, var={self.var}, children=['
        if self.children:
            for c in self.children:
                string += str(c) + ","
            string = string[:-1]
            string += "])"
        else:
            string += "])"
        return string
    # def __repr__(self) -> str:
    #     string = f'Line {self.name}({self.real_root}):\n'
    #     if self.children:
    #         for c in self.children:
    #             string += "\t-> " + str(c) + "\n"
    #         string = string[:-1]
    #     return string


######## AUXILIARY PARSE FUNCTIONS ########

def args_in_brackets(string: str):
    brackets = 0
    rect = 0
    start = 0
    last = False
    matches = []
    real = []
    string = string.strip()

    for i in range(len(string)):
        if string[i] == '(':
            brackets += 1
        elif string[i] == ')':
            brackets -= 1
        elif string[i] == '[':
            rect += 1
            possibilities = []
            real_possibilities = []
            start = i + 1
        elif string[i] == ']':
            rect -= 1
            match = string[start:i].strip()
            real_possibilities.append(match)
            if match and match[0] == "(" and match[-1] == ")":
                match = match[1:-1].strip().replace("'","").replace("\"","")
            possibilities.append(match)
            matches.append(possibilities)
            real.append(real_possibilities)
            start = i + 1
            last = True
        elif string[i] == "," and not brackets:
            if not last:
                match = string[start:i].strip()
                real_match = match
                if match[0] == "(" and match[-1] == ")":
                    match = match[1:-1].strip().replace("\"","").replace("'","")
                if rect:
                    real_possibilities.append(real_match)
                    possibilities.append(match)
                else:
                    matches.append(match)
                    real.append(real_match)
            else:
                last = False
            start = i + 1

    if brackets != 0:
        return None

    if start < len(string):
        match = string[start:len(string)].strip()
        real.append(match)
        if match and match[0] == "(" and match[-1] == ")":
            match = match[1:-1].strip().replace("\"","").replace("'","")
        matches.append(match)

    return matches, real

def check_underscore_args(function: str, arg: str) -> str:
    variations = ["all", "at", "if"]
    var = function.partition("_")[2]

    if var in variations:
        arg = var + "$" + arg

    return arg

def redundant_conditions(condition: str) -> List[str]:
    conditions = []
    final = []

    if "str_detect"in condition:    # TODO integrate this
        return [condition]

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
    if "str_detect" in condition:       # TODO integrate this
        return [condition]

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
            if comparator in condition:

                parts = condition.split(comparator)
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


######## SKETCH CLASS ########

class Sketch:

    def __init__(self, sketch) -> None:
        self.sketch = sketch
        self.lines = sketch.splitlines()
        self.min_loc = 0
        self.max_loc = 0
        self.lines_encoding = {}
        self.select = {}
        self.free_children = []
        self.free_lines = []
        self.aggrs = []
        self.flag_types = flag_types

    def sketch_parser(self, tables: List[str], columns: List[str] = None) -> None:
        logger.info("Parsing sketch...")

        for table in tables:
            table = table.split(".")[0].split("/")[-1]
            tables_names.append(table)

        global columns_names
        columns_names = columns
        parsed = True

        for sketch_line in self.lines:
            sketch_line = sketch_line.strip()

            if sketch_line.startswith("out"):
                line = sketch_line.partition("=")[2]

                if "order by" in line:
                    try:
                        hole = False
                        new_args = []
                        line = line.partition("order by")
                        args = args_in_brackets(line[2].split('(')[1].split(')')[0])[0]
                        if not args:
                            logger.error('Order by cannot be empty')
                            raise RuntimeError()
                        for arg in args:
                            if arg == "??":
                                hole = True
                            else:
                                new_args.append(arg)

                        if new_args and not hole:
                        # if new_args:        # TODO take order into account
                            # if hole and len(columns_names) != len(new_args):
                            #     e_cols = [x for x in columns_names if x not in new_args]
                            #     perms = util.get_permutations(e_cols, len(columns_names)-len(new_args))
                            #     new_args = []
                            #     for perm in perms:
                            #         new_args.append(perm)
                            self.select["arrange"] = new_args
                        line = line[0]
                    except:
                        logger.error('Could not parse select line', sketch_line)
                        parsed = False
                else:
                    self.select["arrange"] = []

                try:
                    args = args_in_brackets(line.split('(')[1].split(')')[0])[0]
                    if args:
                        self.select["cols"] = args
                except:
                    logger.error('Could not parse select line', sketch_line)
                    parsed = False

                if "select distinct" in line:
                    self.select["distinct"] = [' %>% distinct()']
                elif "select ??" not in line:
                    self.select["distinct"] = ['']

            elif sketch_line.startswith("??"):
                if sketch_line == "??":
                    self.max_loc += 1
                    self.min_loc += 1

                elif sketch_line == "??+":
                    self.max_loc = float('inf')
                    self.min_loc += 1

                elif sketch_line == "??*":
                    self.max_loc = float('inf')

                else:
                    logger.error('Sketch line "%s" could not be parsed', sketch_line)
                    parsed = False
                    break

            else:
                line_type = None
                self.min_loc += 1
                self.max_loc += 1
                line = sketch_line.partition("=")
                name = line[0].replace(" ", "")
                if "(" not in line and ")" not in line and "??" in line:
                    args = []
                    real = []
                    function = "??"
                else:
                    string = line[2].strip().partition("(")[2].rpartition(")")[0]
                    args, real = args_in_brackets(string)
                    line = line[2].partition("(")
                    function = line[0].replace(" ", "")
                real_function = function

                if not args and function != "??":
                    logger.error('Sketch line "%s" has missing brackets', sketch_line)
                    parsed = False
                    break

                children = []

                try:
                    if "[" in function: # TODO create more than 1 line and add both to synthesizer
                        # Maybe restrict children vars in creation of leaf since children constraints already does some restrictions
                        functions = args_in_brackets(function)[0]
                        function = functions[0]

                    if "??" == function or isinstance(function, list):
                        # A line with no function. Can have children or not
                        n_children = len(args)

                        if args:
                            line_type = "Free"
                            # Create children with only name and no type or check if it's column(s) / table
                            for arg in args:
                                if "??*" in arg:
                                    line_type = "Incomplete"
                                    n_children -= 1
                                elif "??+" in arg:
                                    line_type = "Incomplete"
                                else:
                                    children.append(Child(arg, "Unknown"))
                            # TODO parse free children and children that we know were they are. we can also roughly know the place in cases of ??*+
                        else:
                            children = None
                            function = None
                            n_children = None
                            line_type = "Empty"

                    elif "natural_join" == function:
                        n_children = 2
                        if len(args) > 4:
                            logger.error('Can only support Natural Join up to 4 tables')
                            parsed = False
                            break
                        else:
                            for n in range(len(args)):
                                children.append(Child(args[n], "Table", real[n]))

                            if len(children) > 2:
                                n_children = len(children)
                                function += str(len(children))

                    elif "inner_join" == function:
                        n_children = 3
                        children.append(Child(args[0], "Table", real[0]))
                        children.append(Child(args[1], "Table", real[1]))
                        children.append(Child(args[2], "JoinCondition", real[2]))

                    elif "anti_join" == function:
                        n_children = 3
                        children.append(Child(args[0], "Table", real[0]))
                        children.append(Child(args[1], "Table", real[1]))
                        if len(args) > 2:
                            children.append(Child(args[2], "Cols", real[2]))
                        else:
                            children.append(Child('', "Cols", ''))

                    elif "left_join" == function or "union" == function or "semi_join" == function:
                        n_children = 2
                        children.append(Child(args[0], "Table", real[0]))
                        children.append(Child(args[1], "Table", real[1]))

                    elif "intersect" == function:   # TODO test
                        n_children = 3
                        children.append(Child(args[0], "Table", real[0]))
                        children.append(Child(args[1], "Table", real[1]))
                        children.append(Child(args[2], "Col", real[2]))

                    elif "cross_join" == function:
                        n_children = 3
                        children.append(Child(args[0], "Table", real[0]))
                        children.append(Child(args[1], "Table", real[1]))
                        children.append(Child(args[2], "CrossJoinCondition", real[2]))

                    elif "unite" == function:
                        n_children = 3
                        children.append(Child(args[0], "Table", real[0]))
                        children.append(Child(args[1], "Col", real[1]))
                        children.append(Child(args[2], "Col", real[2]))

                    elif "filter" == function:
                        n_children = 2
                        children.append(Child(args[0], "Table", real[0]))
                        children.append(Child(args[1], "FilterCondition", real[1]))

                    elif "summarise" in function:
                        n_children = 3
                        arg = check_underscore_args(function, args[1])
                        function = "summarise"

                        children.append(Child(args[0], "Table", real[0]))
                        children.append(Child(arg, "SummariseCondition", real[1]))

                        if len(args) > 2:
                            children.append(Child(args[2], "Cols", real[2]))
                        else:
                            children.append(Child('', "Cols", ''))

                    elif "mutate" in function:
                        n_children = 2
                        arg = check_underscore_args(function, args[1])
                        function = "mutate"

                        children.append(Child(args[0], "Table", real[0]))
                        children.append(Child(arg, "SummariseCondition", real[1]))

                    else:
                        logger.error('Sketch line "%s" could not be parsed', sketch_line)
                        parsed = False
                        break

                except IndexError:
                    logger.error('Sketch line "%s" has not enough arguments', sketch_line)
                    parsed = False
                    break

                if n_children and n_children < len(args) and line_type != "Incomplete" and parsed:
                    logger.error('Sketch line "%s" has too many arguments', sketch_line)
                    parsed = False
                    break

                line = Line(self.max_loc, name, function, children, n_children, line_type, real_function)

                if self.max_loc != float('inf'):
                    self.lines_encoding[self.max_loc] = line
                else:
                    self.free_lines.append(line)

                logger.debug("Sketch creation: " + str(line))

        if not parsed:
            raise RuntimeError("Could not parse sketch")

    def fill_vars(self, spec, line_productions) -> None:
        for line in self.lines_encoding.values():
            if line.line_type != "Empty":
                for root_name in line.root:
                    if root_name != "??":
                        prod = spec.get_function_production(root_name)

                        if prod:
                            line.var.append(prod.id)        # Reduce children seeing func
                        else:
                            logger.error('Unknown function production "%s"', root_name)
                            raise RuntimeError("Could not process sketch production")

                    # reduce number of possible functions in root
                    elif line.line_type:    # Free or Incomplete and has children
                        productions = spec.get_function_productions()
                        for production in productions:
                            if production.lhs.name == 'Empty':
                                continue

                            if line.line_type == "Free" and len(
                                    production.rhs) == line.n_children or line.line_type == "Incomplete" and len(
                                    production.rhs) >= line.n_children:
                                line.var.append(production.id)
                            else:
                                continue

                            if flag_types:
                                if line.children_types and not production.has_in_rhs(line.children_types):
                                    line.var = line.var[:-1]

                        if len(line.var) > 0:
                            line.options = True


                n_children = line.n_children
                children = []

                for c in range(spec.max_rhs):

                    if c < n_children:

                        child = line.get_child(c)

                        for n in range(len(child.names)):
                            prod_name = child.names[n]
                            prod_type = child.type

                            if prod_name != "??":
                                if prod_type == "Table":
                                    prod = spec.get_param_production(prod_name)
                                    if prod:
                                        child.var.append(prod.id)
                                    else:
                                        logger.error('Unknown Table production "%s"', prod_name)
                                        raise RuntimeError("Could not process sketch production")
                                elif prod_type == "Line":
                                    prod = line_productions[prod_name][0]       # check type if not more line prods
                                    if prod:
                                        child.var.append(prod.id)
                                    else:
                                        logger.error('Unknown Line production "%s"', prod_name)
                                        raise RuntimeError("Could not process sketch production")
                                else:
                                    prod = None
                                    if prod_type != "Unknown":
                                        prod_type = spec.get_type(prod_type)
                                        for name in child.productions[n]:
                                            prod = spec.get_enum_production(prod_type, name)
                                            if prod:
                                                child.var.append(prod.id)
                                                break
                                    else:
                                        for name in child.productions[n]:
                                            prod = spec.get_enum_production_with_rhs(name.replace("'", ""))
                                            if prod:
                                                for p in prod:
                                                    child.var.append(p.id)  # Not very efficient
                                                break

                                    if not prod:
                                        logger.error('Unknown %s production "%s"', prod_type, prod_name)
                                        raise RuntimeError("Could not process sketch production")

                            elif flag_types and prod_type != "Unknown":       # Hole with known type
                                if prod_type == "Table":
                                    child.line = True
                                    prod = spec.get_param_productions()
                                    for p in prod:
                                        child.var.append(p.id)

                                else:
                                    prod = spec.get_productions_with_lhs(prod_type)
                                    for p in prod:
                                        child.var.append(p.id)   # Not very efficient?

                            if line.line_type and child.var and n < 1:      # So that all productions when unordered can be in each hole
                                children.append(child.var)

                    else:
                        child = Child()
                        if root_name != "??" or line.line_type == "Free":
                            child.var.append(0)
                        line.add_child(child)

                # In case unordered add all children to the same child
                if line.line_type is not None:
                    for c in range(spec.max_rhs):
                        child = line.get_child(c)
                        if c >= n_children and line.line_type == "Free":
                            break
                        elif "??" not in child.names:
                            child.var = children            # this makes var like [[],[]]
                        child.list_vars = child.var

        logger.debug(self.lines_encoding)