#! /bin/bash



pj_name=$1
py_version=$2

git clone -b ${pj_name} --single-branch https://github.com/marinelay/python_benchmark_github.git

pwd=$PWD

if cd python_benchmark_github; then
    pyenv install ${py_version}
    pyenv virtualenv ${py_version} ${pj_name}
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    source ~/.bashrc

    pyenv activate ${pj_name}
    pyenv local ${pj_name}
    pip install -r requirements.txt
    pyenv deactivate

    cd ${pwd}

    mv python_benchmark_github ${pj_name}
fi