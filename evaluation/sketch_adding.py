import re
import signal
import sys
import time

import os
import yaml
import random
import glob
import subprocess
from squares.dsl.sketch import Sketch

last = ""
functions = ['natural_join', 'inner_join', 'anti_join', 'left_join', 'union', 'intersect', 'semi_join', 'cross_join', 'unite', 'filter', 'summarise', 'mutate']

def signal_handler(sig, frame):
    print('Current File: ' + last)
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class literal(str):
    pass

def literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(literal, literal_presenter)


##### Functions to add holes #####

# def sketch_completed(sketch, spec):
#     sketch_out = ''
#     for line in sketch.lines_encoding:
#         root = sketch.lines_encoding[line]
#         sketch_out += f'{root.name} = {root.real_root}('
#         for child in root.children:
#             if child.real_name:
#                 sketch_out += f'{child.real_name}, '
#         sketch_out = sketch_out[:-2] + ")\n"
#
#     sketch_out += spec['full_sketch'].splitlines()[-1]
#
#     return sketch_out

# number = round(len(lines) * random.randint(0, 20) / 100) # 20%
# k = random.choice(functions)
# v = random.randint(0, len(lines[k]))
# if random.choices([0, 1], [0.8, 0.2])[0]:
#     sketch_out += f'{child.real_name}, '

random.seed(20)

def sketch_no_children(sketch, spec):
    sketch_out = ''
    for line in sketch.lines_encoding:
        root = sketch.lines_encoding[line]
        sketch_out += f'{root.name} = {root.real_root}('
        sketch_out += f'??, ' * len(root.children)
        sketch_out = sketch_out[:-2] + ")\n"

    sketch_out += spec['full_sketch'].splitlines()[-1]

    return sketch_out

def sketch_no_root(sketch, spec):
    sketch_out = ''
    for line in sketch.lines_encoding:
        root = sketch.lines_encoding[line]
        sketch_out += f'{root.name} = ??('
        for child in root.children:
            if child.real_name:
                sketch_out += f'{child.real_name}, '
            else:
                sketch_out += f'\'\', '
        sketch_out = sketch_out[:-2] + ")\n"

    sketch_out += spec['full_sketch'].splitlines()[-1]

    return sketch_out

def sketch_no_filter(sketch, spec):
    sketch_out = ''
    for line in sketch.lines_encoding:
        root = sketch.lines_encoding[line]
        if root.real_root == "filter":
            sketch_out += f'{root.name} = ??\n'
        else:
            sketch_out += f'{root.name} = {root.real_root}('
            for child in root.children:
                if child.real_name:
                    sketch_out += f'{child.real_name}, '
            sketch_out = sketch_out[:-2] + ")\n"

    sketch_out += spec['full_sketch'].splitlines()[-1]

    return sketch_out

def sketch_no_summarise(sketch, spec):
    sketch_out = ''
    for line in sketch.lines_encoding:
        root = sketch.lines_encoding[line]
        if root.real_root == "summarise":
            sketch_out += f'{root.name} = ??\n'
        else:
            sketch_out += f'{root.name} = {root.real_root}('
            for child in root.children:
                if child.real_name:
                    sketch_out += f'{child.real_name}, '
            sketch_out = sketch_out[:-2] + ")\n"

    sketch_out += spec['full_sketch'].splitlines()[-1]

    return sketch_out

# NOTE: Don't forget to copy sketch if we're going to change variables

######################################################

def parse_sketch(instances):
    global last
    all = []
    for file in instances:
        last = file
        with open(file, "r+") as f:
            spec = yaml.safe_load(f)

            if 'full_sketch' in spec:
                all.append(file)

                out = {}
                sketch = Sketch(spec['full_sketch'])
                inputs = spec['inputs']
                sketch.sketch_parser(inputs)

                if not 'sketch_no_children' in spec:
                    out['sketch_no_children'] = literal(sketch_no_children(sketch, spec))

                # Attention when anti_join or summarise since 2 or 3 args
                if not 'sketch_no_root' in spec:
                    out['sketch_no_root'] = literal(sketch_no_root(sketch, spec))

                if not 'sketch_no_filter' in spec:
                    out['sketch_no_filter'] = literal(sketch_no_filter(sketch, spec))

                if not 'sketch_no_summarise' in spec:
                    out['sketch_no_summarise'] = literal(sketch_no_summarise(sketch, spec))

                if out != {}:
                    output = yaml.dump(out, default_flow_style=False, sort_keys=False)
                    f.write("\n" + output)

    # print(all)


# def remove_sketch(instances):
#     global last
#     for file in instances:
#         last = file
#         with open(file, "r") as f:
#             spec = yaml.safe_load(f)
#
#         if 'sketch_no_children' in spec:
#             del spec['sketch_no_children']
#
#         # Attention when anti_join or summarise since 2 or 3 args
#         if 'sketch_no_root' in spec:
#             del spec['sketch_no_root']
#
#         if 'sketch_no_filter' in spec:
#             del spec['sketch_no_filter']
#
#         if 'sketch_no_summarise' in spec:
#             del spec['sketch_no_summarise']
#
#         with open(file, "w") as f:
#             output = yaml.dump(spec)
#             f.write(output)

def run_get_result():
    # for file in glob.glob('tests-examples/**/**/*.yaml', recursive=True):
    global last
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
                        process = subprocess.run(["python3", "sequential.py", file], timeout=600, stderr=subprocess.DEVNULL, check=True, stdout=subprocess.PIPE, universal_newlines=True)
                    except subprocess.TimeoutExpired:
                        print(file)
                        continue

                    output = process.stdout
                    output = output.split("\n\n")[2]

                    instance['sketch'] = literal(output)    # prints with - because it's list
                    output = yaml.dump(instance, default_flow_style=False, sort_keys=False)
                    f.write("\n" + output)

def get_comments(instances):
    global last
    for file in instances:
        last = file

        with open(file, "r") as f:
            spec = yaml.safe_load(f)

            if 'sql' in spec:
                out = {}
                comment = spec['sql']

                out[file] = literal(comment)

                output = yaml.dump(out, default_flow_style=False, sort_keys=False)
                # with open("evaluation/file_extractions/tb_sql.yaml", "a") as tb:
                #     tb.write(output + "\n")

if __name__ == '__main__':
    # parse_sketch(['tests-examples/textbook/31.yaml'])
    # parse_sketch(glob.glob('tests-examples/textbook/*.yaml'))
    # parse_sketch(glob.glob('tests-examples/scythe/top_rated_posts/*.yaml'))
    parse_sketch(glob.glob('tests-examples/scythe/recent_posts/*.yaml'))