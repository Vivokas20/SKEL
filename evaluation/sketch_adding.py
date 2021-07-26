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

def sketch_only_filter(sketch, spec):
    sketch_out = ''
    for line in sketch.lines_encoding:
        root = sketch.lines_encoding[line]
        if root.real_root != "filter":
            sketch_out += f'{root.name} = ??\n'
        else:
            sketch_out += f'{root.name} = {root.real_root}('
            for i, child in enumerate(root.children):
                if i == 0:
                    sketch_out += f'??, '
                elif child.real_name:
                    sketch_out += f'{child.real_name}, '
            sketch_out = sketch_out[:-2] + ")\n"

    sketch_out += spec['full_sketch'].splitlines()[-1]

    return sketch_out

def sketch_only_summarise(sketch, spec):
    sketch_out = ''
    for line in sketch.lines_encoding:
        root = sketch.lines_encoding[line]
        if root.real_root != "summarise":
            sketch_out += f'{root.name} = ??\n'
        else:
            sketch_out += f'{root.name} = {root.real_root}('
            for i, child in enumerate(root.children):
                if i == 0:
                    sketch_out += f'??, '
                elif child.real_name:
                    sketch_out += f'{child.real_name}, '
            sketch_out = sketch_out[:-2] + ")\n"

    sketch_out += spec['full_sketch'].splitlines()[-1]

    return sketch_out

# NOTE: Don't forget to copy sketch if we're going to change variables

######################################################

def parse_sketch(instances, type_s = None, check = False):
    global last
    all = []
    summarise = []
    filter = []
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

                if check:
                    filter_flag = False
                    summarise_flag = False
                    for line in sketch.lines_encoding:
                        root = sketch.lines_encoding[line]
                        if root.real_root == "summarise" and not summarise_flag:
                            summarise.append(file)
                            summarise_flag = True
                        elif root.real_root == "filter" and not filter_flag:
                            filter.append(file)
                            filter_flag = True

                else:
                    if not 'sketch_no_children' in spec:
                        out['sketch_no_children'] = literal(sketch_no_children(sketch, spec))

                    # Attention when anti_join or summarise since 2 or 3 args
                    if not 'sketch_no_root' in spec:
                        out['sketch_no_root'] = literal(sketch_no_root(sketch, spec))

                    if type_s == "filter":
                        if not 'sketch_no_filter' in spec:
                            out['sketch_no_filter'] = literal(sketch_no_filter(sketch, spec))

                        if not 'sketch_only_filter' in spec:
                            out['sketch_only_filter'] = literal(sketch_only_filter(sketch, spec))

                    if type_s == "summarise":
                        if not 'sketch_no_summarise' in spec:
                            out['sketch_no_summarise'] = literal(sketch_no_summarise(sketch, spec))

                        if not 'sketch_only_summarise' in spec:
                            out['sketch_only_summarise'] = literal(sketch_only_summarise(sketch, spec))

                if out != {}:
                    output = yaml.dump(out, default_flow_style=False, sort_keys=False)
                    f.write("\n" + output)

    if check:
        print("All")
        print(all)
        print("Filter" + str(len(filter)))
        print(filter)
        print("Summarise" + str(len(summarise)))
        print(summarise)


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

def get_output():
    s = glob.glob("evaluation/data/no_sketch/tests-examples/scythe/**/*.log")
    sp = glob.glob("evaluation/data/no_sketch/tests-examples/spider/**/*.log")
    t = glob.glob("evaluation/data/no_sketch/tests-examples/textbook/*.log")

    files = s+sp+t

    for file in files:
        with open(file, "r") as f:
            log = f.read()
            out = {}

            try:
                file_solution = re.search('Solution found: \[(.+)]', log)[0]
                file_solution = file_solution.replace("Solution found: ", "")[1:-1]
                file_select = re.search('out <- df[0-9]+ %>% select(.+)', log)[0]
                file_select = file_select.split("%>% ", 1)[1]

                out[file] = literal(file_solution+"\n"+file_select)

            except:
                continue

        if out:
            with open("solutions.yaml", "a") as tb:
                output = yaml.dump(out, default_flow_style=False, sort_keys=False)
                tb.write(output + "\n")


if __name__ == '__main__':
    # parse_sketch(['tests-examples/textbook/35.yaml'])
    filter = ['tests-examples/textbook/1.yaml', 'tests-examples/textbook/10.yaml', 'tests-examples/textbook/14.yaml', 'tests-examples/textbook/15.yaml', 'tests-examples/textbook/16.yaml', 'tests-examples/textbook/17.yaml', 'tests-examples/textbook/19.yaml', 'tests-examples/textbook/2.yaml', 'tests-examples/textbook/20.yaml', 'tests-examples/textbook/21.yaml', 'tests-examples/textbook/22.yaml', 'tests-examples/textbook/23.yaml', 'tests-examples/textbook/24.yaml', 'tests-examples/textbook/25.yaml', 'tests-examples/textbook/26.yaml', 'tests-examples/textbook/28.yaml', 'tests-examples/textbook/29.yaml', 'tests-examples/textbook/3.yaml', 'tests-examples/textbook/31.yaml', 'tests-examples/textbook/35.yaml', 'tests-examples/textbook/4.yaml', 'tests-examples/textbook/5.yaml', 'tests-examples/textbook/6.yaml', 'tests-examples/textbook/8.yaml', 'tests-examples/textbook/9.yaml', 'tests-examples/scythe/top_rated_posts/002.yaml', 'tests-examples/scythe/top_rated_posts/013.yaml', 'tests-examples/scythe/top_rated_posts/017.yaml', 'tests-examples/scythe/top_rated_posts/025.yaml', 'tests-examples/scythe/top_rated_posts/031.yaml', 'tests-examples/scythe/top_rated_posts/032.yaml', 'tests-examples/scythe/top_rated_posts/038.yaml', 'tests-examples/scythe/top_rated_posts/043.yaml', 'tests-examples/scythe/recent_posts/004.yaml', 'tests-examples/scythe/recent_posts/016.yaml', 'tests-examples/scythe/recent_posts/019.yaml', 'tests-examples/scythe/recent_posts/021.yaml', 'tests-examples/scythe/recent_posts/028.yaml', 'tests-examples/scythe/recent_posts/031.yaml', 'tests-examples/scythe/recent_posts/040.yaml', 'tests-examples/scythe/recent_posts/046.yaml', 'tests-examples/spider/architecture/0007.yaml', 'tests-examples/spider/architecture/0008.yaml', 'tests-examples/spider/architecture/0009.yaml', 'tests-examples/spider/architecture/0011.yaml', 'tests-examples/spider/architecture/0012.yaml', 'tests-examples/spider/architecture/0013.yaml', 'tests-examples/spider/architecture/0017.yaml']
    summarise = ['tests-examples/textbook/10.yaml', 'tests-examples/textbook/14.yaml', 'tests-examples/textbook/15.yaml', 'tests-examples/textbook/17.yaml', 'tests-examples/textbook/18.yaml', 'tests-examples/textbook/2.yaml', 'tests-examples/textbook/22.yaml', 'tests-examples/textbook/23.yaml', 'tests-examples/textbook/25.yaml', 'tests-examples/textbook/26.yaml', 'tests-examples/textbook/29.yaml', 'tests-examples/textbook/3.yaml', 'tests-examples/textbook/4.yaml', 'tests-examples/textbook/5.yaml', 'tests-examples/textbook/6.yaml', 'tests-examples/textbook/7.yaml', 'tests-examples/textbook/8.yaml', 'tests-examples/textbook/9.yaml', 'tests-examples/scythe/top_rated_posts/001.yaml', 'tests-examples/scythe/top_rated_posts/002.yaml', 'tests-examples/scythe/top_rated_posts/004.yaml', 'tests-examples/scythe/top_rated_posts/005.yaml', 'tests-examples/scythe/top_rated_posts/006.yaml', 'tests-examples/scythe/top_rated_posts/007.yaml', 'tests-examples/scythe/top_rated_posts/008.yaml', 'tests-examples/scythe/top_rated_posts/009.yaml', 'tests-examples/scythe/top_rated_posts/011.yaml', 'tests-examples/scythe/top_rated_posts/012.yaml', 'tests-examples/scythe/top_rated_posts/013.yaml', 'tests-examples/scythe/top_rated_posts/014.yaml', 'tests-examples/scythe/top_rated_posts/016.yaml', 'tests-examples/scythe/top_rated_posts/017.yaml', 'tests-examples/scythe/top_rated_posts/019.yaml', 'tests-examples/scythe/top_rated_posts/021.yaml', 'tests-examples/scythe/top_rated_posts/027.yaml', 'tests-examples/scythe/top_rated_posts/028.yaml', 'tests-examples/scythe/top_rated_posts/029.yaml', 'tests-examples/scythe/top_rated_posts/034.yaml', 'tests-examples/scythe/top_rated_posts/036.yaml', 'tests-examples/scythe/top_rated_posts/037.yaml', 'tests-examples/scythe/top_rated_posts/038.yaml', 'tests-examples/scythe/top_rated_posts/043.yaml', 'tests-examples/scythe/top_rated_posts/047.yaml', 'tests-examples/scythe/top_rated_posts/048.yaml', 'tests-examples/scythe/top_rated_posts/049.yaml', 'tests-examples/scythe/top_rated_posts/051.yaml', 'tests-examples/scythe/top_rated_posts/055.yaml', 'tests-examples/scythe/top_rated_posts/057.yaml', 'tests-examples/scythe/recent_posts/004.yaml', 'tests-examples/scythe/recent_posts/007.yaml', 'tests-examples/scythe/recent_posts/009.yaml', 'tests-examples/scythe/recent_posts/011.yaml', 'tests-examples/scythe/recent_posts/012.yaml', 'tests-examples/scythe/recent_posts/016.yaml', 'tests-examples/scythe/recent_posts/021.yaml', 'tests-examples/scythe/recent_posts/028.yaml', 'tests-examples/scythe/recent_posts/032.yaml', 'tests-examples/scythe/recent_posts/040.yaml', 'tests-examples/scythe/recent_posts/045.yaml', 'tests-examples/scythe/recent_posts/051.yaml', 'tests-examples/spider/architecture/0003.yaml', 'tests-examples/spider/architecture/0009.yaml', 'tests-examples/spider/architecture/0011.yaml']
    textbook = glob.glob('tests-examples/textbook/*.yaml')
    top = glob.glob('tests-examples/scythe/top_rated_posts/*.yaml')
    recent = glob.glob('tests-examples/scythe/recent_posts/*.yaml')
    spider = glob.glob('tests-examples/spider/architecture/*.yaml')

    # parse_sketch(textbook + top + recent + spider, check = True)
    # parse_sketch(filter, "filter")
    # parse_sketch(summarise, "summarise")
    get_output()