from logging import getLogger
import re
from typing import List

logger = getLogger('squares')

tables_names = []
df_tables_names = []
lines_names = []

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

    def __repr__(self) -> str:
        return f'Child({self.child}, type={self.type}, var={self.var})'


class Line:
    def __init__(self, name: str = None, root: str = None, children: List[Child] = None) -> None:
        self.name = name
        self.root = root
        self.children = children
        if self.children is not None:
            self.n_children = len(children)
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
    open_b = 0
    close_b = 0
    start = 0
    matches = []

    for i in range(len(string)):
        if string[i] == '(':
            open_b += 1
            if open_b == 1:
                start = i + 1
        close_b += string[i] == ')'
        if open_b > 0 and open_b == close_b:
            open_b = 0
            close_b = 0
            matches.append(string[start:i])

    # matches = re.findall(r'\(+.*?\)+', string)
    # for i in range(len(matches)):
    #     matches[i] = matches[i][1:-1]

    return matches


def split_args(string: str) -> List[str]:
    brackets = 0
    start = 0
    matches = []

    for i in range(len(string)):
        brackets += string[i] == '('
        brackets -= string[i] == ')'
        if string[i] == "," and not brackets:
            matches.append(string[start:i])
            start = i + 1

    matches.append(string[start:len(string)])
    return matches


def check_underscore_args(string: str, func: str, arg: str) -> str:
    matches = re.findall(rf'{func}[^(]*?\(', string)
    match = matches[0].replace(f"{func}", "")[:-1]

    if match:
        arg = match[1:] + "$" + arg

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


############# PARSE FUNCTIONS #############

def check_filter_mutate_summarise(line, name):
    children = []

    new_table = line.split("%>%")[0].replace(" ","")
    args = args_in_brackets(line)

    children.append(Child("Table", new_table))
    if name == "filter":
        children.append(Child("FilterCondition", args[0]))
    elif name == "mutate":
        arg = check_underscore_args(line, name, args[0])
        children.append(Child("SummariseCondition", arg))
    elif name == "summarise":
        arg = check_underscore_args(line, name, args[1])
        children.append(Child("SummariseCondition", arg))
        arg0 = add_quotes(args[0])
        children.append(Child("Cols", arg0))

    return children


def check_union_inner_left_anti_join(line, name):
    children = []
    args = args_in_brackets(line)[0].replace(" ", "")    # If I take spaces Cols gonna fail
    args = split_args(args)

    children.append(Child("Table", args[0]))
    children.append(Child("Table", args[1]))

    if name == "anti_join":
        args2 = args_in_brackets(args[2])[0]
        args2 = add_quotes(args2)
        children.append(Child("Cols", args2))

    elif name == "inner_join":
        args2 = args_in_brackets(args[2])[0]
        args2 = add_quotes(args2)
        children.append(Child("JoinCondition", args2))

    return children


class Sketch:

    def __init__(self, sketch) -> None:
        self.sketch = sketch
        self.lines = sketch.splitlines()
        self.loc = len(self.lines) - 1
        self.lines_encoding = []
        self.functions = []

    def sketch_parser(self, names: List[str]) -> None:
        parsed = True

        # TODO verificar os types
        # TODO if none function - ??

        # arguments have to be spaced
        for table in names:
            table = table.split(".")[0].split("/")[-1]
            tables_names.append(table)

        for sketch_line in self.lines[:-1]:
            line = sketch_line.split("<-")
            name = line[0].replace(" ", "")
            line = line[1]
            root = None
            children = None

            if "natural_join" in line: #eval all natural_joins cause they're too special
                root = "natural_join"
                children = check_union_inner_left_anti_join(line, root)
                pass

            elif "summarise" in line:
                root = "summarise"
                children = check_filter_mutate_summarise(line, root)

            elif "anti_join" in line:
                root = "anti_join"
                children = check_union_inner_left_anti_join(line, root)

            elif "left_join" in line:
                root = "left_join"
                children = check_union_inner_left_anti_join(line, root)

            elif "bind_rows" in line:   #eval_union
                root = "union"
                children = check_union_inner_left_anti_join(line, root)

            elif "intersect" in line:  #after natural_joins and it appears in select (out)!
                pass

            elif "semi_join" in line:
                root = "semi_join"
                children = check_union_inner_left_anti_join(line, root)

            elif "inner_join" in line:  #after natural_joins
                root = "inner_join"
                children = check_union_inner_left_anti_join(line, root)

            elif "mutate" in line:  #after inner_join
                root = "mutate"
                children = check_filter_mutate_summarise(line, root)

            elif "full_join" in line:  #cross_join(Table, Table, CrossJoinCondition)  #after natural_joins
                root = "cross_join"
                pass

            elif "filter" in line:  #after full_join
                root = "filter"
                children = check_filter_mutate_summarise(line, root)

            elif "unite" in line:
                pass

            else:
                name = None
                logger.warning('Sketch line "%s" not be completely parsed', sketch_line)

            if root is not None:
                self.functions.append(root)

            self.lines_encoding.append(Line(name, root, children))
            print(self.lines_encoding[-1])
        if not parsed:
            logger.warning('Sketch could not be completely parsed')

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
