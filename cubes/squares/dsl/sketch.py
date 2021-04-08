from logging import getLogger
import re

logger = getLogger('squares')

tables_names = []
lines_names = []

class Child:
    def __init__(self, child_type = None, child = None):
        self.child = child
        self.type = None
        if child_type is not None and child is not None:
            self.check_type(child_type)
            self.var = None
        else:
            self.var = 0

    def get_name(self):
        return self.child

    def get_type(self):
        return self.type

    def check_type(self, child_type):
        self.type = child_type

        if child_type == "Table":
            for i in range(len(tables_names)):
                if tables_names[i] in self.child:
                    self.child = i
                    break

            for i in range(len(lines_names)):
                if lines_names[i] in self.child:
                    self.child = i
                    self.type = "Line"
                    break


class Line:
    def __init__(self, name, root, children):
        self.name = name
        self.root = root
        self.children = children
        self.n_children = len(children)
        self.var = None
        lines_names.append(name)

    def get_root(self):
        return self.root

    def get_n_children(self):
        return self.n_children

    def get_child(self, n):
        return self.children[n]

    def add_child(self, child):
        return self.children.append(child)


def args_in_brackets(string):
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

class Sketch:

    def __init__(self, sketch):
        self.sketch = sketch
        self.lines = sketch.splitlines()
        self.loc = len(self.lines) - 1
        self.lines_encoding = []
        self.functions = []

    def check_summarise(self, line):
        # TODO implement the summarise_
        root = "summarise"
        children = []
        line = line.split("<-")
        name = line[0].replace(" ", "")

        new_table = line[1].split("%>%")[0].replace(" ","")

        args = args_in_brackets(line[1])

        children.append(Child("Table", new_table))
        children.append(Child("SummariseCondition", args[1]))
        children.append(Child("Cols", args[0]))

        self.lines_encoding.append(Line(name, root, children))

    def check_left_join(self, line):
        root = "left_join"
        children = []
        line = line.split("<-")
        name = line[0].replace(" ", "")

        args = args_in_brackets(line[1])[0].replace(" ", "").split(",")

        children.append(Child("Table", args[0]))
        children.append(Child("Table", args[1]))

        self.lines_encoding.append(Line(name, root, children))

    def check_filter(self, line):
        root = "filter"
        children = []
        line = line.split("<-")
        name = line[0].replace(" ", "")

        new_table = line[1].split("%>%")[0].replace(" ","")

        args = args_in_brackets(line[1])

        children.append(Child("Table", new_table))
        children.append(Child("FilterCondition", args[0]))

        self.lines_encoding.append(Line(name, root, children))

    def sketch_parser(self, names):
        parsed = True

        # TODO verificar os types
        # TODO if none function - ??

        # table names and columns cannot have ()
        # arguments have to be spaced

        for table in names:
            tables_names.append(table.split(".")[0].split("/")[-1])

        for line in self.lines[:-1]:
            if "left_join" in line:
                self.functions.append("left_join")
                self.check_left_join(line)

            elif "filter" in line:
                self.functions.append("filter")
                self.check_filter(line)

            elif "summarise" in line:
                self.functions.append("summarise")
                self.check_summarise(line)

            else:
                parsed = False

        if not parsed:
            logger.warning('Sketch could not be completely parsed')

    def fill_vars(self, spec, line_productions):
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
                                logger.warning('Unknown table production "%s"', prod_name)
                        elif prod_type == "Line":
                            prod = line_productions[prod_name][0]       # check type if not more line prods
                            if prod:
                                child.var = prod.id
                            else:
                                logger.warning('Unknown line production "%s"', prod_name)
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
