import time
import requests
import json
import pdb
import datetime
import utils
import pprint
from config import *

ROOT_DIR = os.getcwd()

if __name__ == '__main__':
    repos = [os.path.basename(rj)[:-5] for rj in glob.glob(f"{ROOT_DIR}/data/pr_data/*.json")]

    test_num = 0
    for repo in repos:
        jsonfile = utils.read_json_from_file(f"{ROOT_DIR}/data/pr_data/{repo}.json")

        test_num += len(jsonfile)

    print(test_num)