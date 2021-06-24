import os, sys, glob
import time
import argparse
import re
import requests
from bs4 import BeautifulSoup
from easyprocess import EasyProcess
from functools import partial
from config_crawl import *
from config import *

repo_search_url = "https://api.github.com/search/repositories?q=" #q=python"
search = "language:python+license:Apache-2.0+license:MIT+license:BSD-3-Clause&sort=stars"
backoff = 2.05

if __name__ == '__main__':
    i = 1
    repos = []
    logfile = open("repo_url.txt", 'w')
    while True:
        search_url = f"{repo_search_url}+{search}&page={i}&per_page=100"
        res = requests.get(search_url, auth=(username, token), headers=headers)
        if res.status_code == 500 or res.status_code == 404 or res.status_code == 422:
            print(f"{ERROR}: {res.status_code}")
            break

        if res.status_code == 429:
            time.sleep(backoff)
            continue

        items = json.loads(res.content.decode("utf-8"))["items"]
        for item in items:
            repo_url = item["html_url"]
            number_of_stars = item["stargazers_count"]

            if number_of_stars < 10000 :
                exit()

            print(f"{PROGRESS}: checking {repo_url} ... {number_of_stars} stars")
            if "sample" in repo_url or "example" in repo_url or "tutorial" in repo_url:
                print(f"{FAIL}: {repo_url} is example github")
                continue
            else :
                print(f"{SUCCESS}: {repo_url} is useful project")
                logfile.write(f"{repo_url}\n")

        i = i + 1
