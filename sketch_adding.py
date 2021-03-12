import glob
import yaml

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
                    sketch = []
                    instance = {}

                    for l in spec['comment'].splitlines():
                        if (l.startswith("df") or l.startswith("out")) and "<-" in l:
                            sketch.append(l)
                            if l.startswith("out"):
                                break

                    instance['sketch'] = sketch
                    output = yaml.dump(instance, default_flow_style=False, sort_keys=False)
                    with open(file, 'a') as out:
                        out.write(output)
                    out.close()
            else:
                no_comment.append(file)