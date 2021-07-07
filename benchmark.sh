#! /bin/bash

pj_name=$1
py_version=$2

git clone -b ${pj_name} --single-branch https://github.com/marinelay/python_benchmark_github.git

pwd=$PWD

cd python_benchmark_github

pyenv install ${py_version}
pyenv virutalenv ${py_version} ${pj_name}
pyenv local ${pj_name}
pip install -r requirements.txt

cd ${pwd}

mv python_benchmark_github ${pj_name}