#! /bin/bash
pj=$1


jq -r '.'${pj}' | .[] | @base64' benchmark.json | while read i; do
    _jq() {
        echo ${i} | base64 --decode | jq -r ${1}
    }

    pj_name=$(_jq '.name')
    py_version=$(_jq '.python')

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
done

