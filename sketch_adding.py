import signal
import sys
import time
import yaml
import subprocess

last = ""

class literal(str):
    pass


def literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(literal, literal_presenter)


def signal_handler(sig, frame):
    print('Current File: ' + last)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
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