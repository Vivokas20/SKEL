import signal
import sys
import time
import yaml
import random
import glob
import subprocess

last = ""

class literal(str):
    pass


def literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(literal, literal_presenter)

def args_in_brackets(string: str):
    brackets = 0
    rect = 0
    start = 0
    last = False
    matches = []
    string = string.strip()

    for i in range(len(string)):
        if string[i] == '(':
            brackets += 1
        elif string[i] == ')':
            brackets -= 1
        elif string[i] == '[':
            rect += 1
            possibilities = []
            start = i + 1
        elif string[i] == ']':
            rect -= 1
            match = string[start:i].strip()
            if match and match[0] == "(" and match[-1] == ")":
                match = match[1:-1].strip().replace("'","")
            possibilities.append(match)
            matches.append(possibilities)
            start = i + 1
            last = True
        elif string[i] == "," and not brackets:
            if not last:
                match = string[start:i].strip()
                if match[0] == "(" and match[-1] == ")":
                    match = match[1:-1].strip().replace("'","")
                if rect:
                    possibilities.append(match)
                else:
                    matches.append(match)
            else:
                last = False
            start = i + 1

    if brackets != 0:
        return None

    if start < len(string):
        match = string[start:len(string)].strip()
        if match and match[0] == "(" and match[-1] == ")":
            match = match[1:-1].strip().replace("'","")
        matches.append(match)

    return matches

class Line:
    def __init__(self, name: str, function: str, children: str) -> None:
        self.name = name
        self.function = function
        self.children = children

    def __repr__(self) -> str:
        string = f'{self.name} = {self.function}('
        for c in self.children:
            if isinstance(c, list):
                string += "(" + str(c) + ")"
            else:
                string += str(c)
            string += ","
        string = string[:-1]
        string += ")"
        return string

def make_sketch():
    # with open("all_dirs.txt") as dirs:
    #     for file in dirs:
    #         file = file[:-1]
    #         last = file
    #         if 'schema.yaml' in file:
    #             continue

    # with open(file, "r+") as f:
    with open("tests-examples/demo/test.yaml", "r+") as f:
        spec = yaml.safe_load(f)

        if 'full_sketch' in spec:
            instances = {}

            lines = {}
            n_children = 0
            functions = []
            sketch = spec['full_sketch'].splitlines()
            for line in sketch:
                line = line.partition("=")[2].strip().partition("(")
                args = args_in_brackets(line[2].rpartition(")")[0])
                func = line[0].replace(" ", "")
                lines[func] = args
                functions.append(func)
                n_children += len(args)

            if not 'sketch_easy' in spec:
                '''
                holes in at least 1 up to 60% of children
                holes in up to 20% of lines
                can't have missing lines or unfinished lines
                '''

                ### Children ###
                number = round(n_children * random.randint(0, 60) / 100)
                if number == 0:
                    number = 1

                for n in range(0, number):
                    choice = "??"
                    while choice == "??":
                        k = random.choice(list(lines.keys()))
                        v = random.randint(0, len(lines[k]))
                        choice = lines[k][v]
                    new = lines[k]
                    new[v] = "??"
                    lines[k] = new

                ### Functions ###
                number = round(len(lines) * random.randint(0, 20) / 100)

                for n in range(0, number):
                    choice = "??"
                    while choice == "??":
                        k = random.choice(functions)
                        v = random.randint(0, len(lines[k]))
                        choice = lines[k][v]
                    new = lines[k]
                    new[v] = "??"
                    lines[k] = new

                sketch = ""
                instances['sketch_easy'] = literal(sketch)

            if not 'sketch_mid' in spec:
                sketch = ""
                instances['sketch_mid'] = literal(sketch)

            if not 'sketch_hard' in spec:
                sketch = ""
                instances['sketch_hard'] = literal(sketch)

            # output = yaml.dump(instances, default_flow_style=False, sort_keys=False)
            # f.write("\n" + output)

# def signal_handler(sig, frame):
#     print('Current File: ' + last)
#     sys.exit(0)
#
# signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)
#
def run_get_result():
    # for file in glob.glob('tests-examples/**/**/*.yaml', recursive=True):
    with open("test_dirs.txt") as dirs:
        for file in dirs:
            file = file[:-1]
            last = file
            if 'schema.yaml' in file:
                continue

            with open(file, "r+") as f:
                spec = yaml.safe_load(f)

                if 'sketch' not in spec:
                    instance = {}

                    try:
                        # cubes and test_examples in same directory
                        process = subprocess.run(["python3", "cubes/sequential.py", file], timeout=600, stderr=subprocess.DEVNULL, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                    except subprocess.TimeoutExpired:
                        print(file)
                        continue

                    output = process.stdout
                    output = output.split("\n\n")[2]

                    instance['sketch'] = literal(output)    # prints with - because it's list
                    output = yaml.dump(instance, default_flow_style=False, sort_keys=False)
                    f.write("\n" + output)

def get_comments():
    instances = glob.glob('tests-examples/textbook/*.yaml')
    for file in instances:
        with open(file, "r") as f:
            spec = yaml.safe_load(f)

            if 'sql' in spec:
                out = {}

                comment = spec['sql']

                out[file] = literal(comment)

                output = yaml.dump(out, default_flow_style=False, sort_keys=False)
                with open("evaluation/file_extractions/tb_sql.yaml", "a") as tb:
                    tb.write(output + "\n")

if __name__ == '__main__':
    get_comments()
