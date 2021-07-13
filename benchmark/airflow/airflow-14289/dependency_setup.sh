sudo apt-get install -y apt-utils mysql-server libmysqlclient-dev libxml2 libpq-dev libkrb5-dev libsasl2-dev unixodbc-dev libldap2-dev
export SLUGIFY_USES_TEXT_UNIDECODE=yes

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

pip install --upgrade pip
pip install -r ../requirements.txt
pip install -e ".[devel]"
export PYTHONIOENCODING=utf-8

airflow db init