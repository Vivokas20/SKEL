import glob
import yaml

class literal(str):
    pass


def literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

yaml.add_representer(literal, literal_presenter)

if __name__ == '__main__':
    no_comment = []

    for file in glob.glob('tests-examples/**/**/*.yaml', recursive=True):
    # file = "tests-examples/demo/demo.yaml"
        if 'schema.yaml' in file:
            pass

        with open(file) as f:
            spec = yaml.safe_load(f)

            if 'comment' in spec:
                if 'sketch' not in spec:
                    sketch = ""
                    instance = {}

                    for l in spec['comment'].splitlines():
                        if (l.startswith("df") or l.startswith("out")) and "<-" in l:
                            sketch += str(l) + "\n"
                            if l.startswith("out"):
                                break

                    instance['sketch'] = literal(sketch)
                    output = yaml.dump(instance, default_flow_style=False, sort_keys=False)
                    with open(file, 'a') as out:
                        out.write("\n" + output)
                    out.close()
            else:
                no_comment.append(file)