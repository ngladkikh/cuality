# cuality
Python projects analysis

## Installation

1. Go to source dir
2. create venv: `python -m venv venv`. Name of virtual environment is hardcoded at the moment
3. install dependencies: `pip install -r requirements.txt`
4. Install dot files builder [Graphviz](https://graphviz.org/).

## Usage

1. Invoke bash script:

    ```bash
    ./classes-uml.sh [path-to-package]
    ```
    
    Where `path-to-package` is path to the package you want to analyse.

2. Open `output` dir and find `*.png` files with diagrams.
