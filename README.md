# SKEL - A Sketch-based SQL Synthesizer Using Query Reverse Engineering

Given a set of input-output examples (tables) and a sketch (incomplete query), SKEL returns the desired query in R and in SQL.

    
# Usage

## Using CLI:
```
usage: sequential.py [--sketch=SKETCH] [--flag_types] [--generate_sketch_dsl] SPECIFICATION

positional arguments:
  SPECIFICATION  specification yaml file

optional arguments:
  -h, --help              shows a help message and exits
  --sketch [SKETCH]       name of the sketch in the specification file (default: None)
  --flag_types            use types optimization to parse sketch
  --generate_sketch_dsl   generate dsl using sketch productions

```


# Installation

### Prerequisites
- Python 3.6+
- R 3.6.3

## Using `setup.py` and `setup.r`

- Create a new virtual environment (strongly recommended):
  ```
  python3 -m venv env
  ```

- Install python dependencies:
  ```
  pip install .
  ```
  
- Install R dependencies:
  ```
  Rscript setup.r
  ```