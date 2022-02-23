#!/bin/bash


BASE="./venv/bin"

$BASE/python -m pylint -ry \
    --disable=all \
    --enable=imports,RP0402 \
    --import-graph=./output/imports_all.dot \
    --ext-import-graph=./output/imports_ext.dot \
    --int-import-graph=./output/imports_int.dot \
    "$1" && \
dot -Tpng ./output/imports_int.dot -y -o ./output/imports_int.png

$BASE/pyreverse -d output --colorized -k "$1" && \
dot -Tpng ./output/classes.dot -y -o ./output/classes.png &&\
dot -Tpng ./output/packages.dot -y -o ./output/packages.png
