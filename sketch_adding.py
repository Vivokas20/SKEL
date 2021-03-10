import glob
import yaml

if __name__ == '__main__':
    no_sql = []

    for file in glob.glob('tests-examples/**/**/*.yaml', recursive=True):
    # file = "tests-examples/demo/demo.yaml"
        if 'schema.yaml' in file:
            pass

        with open(file) as f:
            spec = yaml.safe_load(f)

            if 'sql' in spec:
                if 'sketch' not in spec:
                    with open(file, 'a') as file:
                        sketch = "\nsketch: |\n"
                        # yaml.dump(spec['sql'],file)
                        for l in spec['sql'].split("\n"):
                            sketch += "  " + l + "\n"
                        print(sketch)
                        file.write(sketch)
                    file.close()

            else:
                no_sql.append(file)