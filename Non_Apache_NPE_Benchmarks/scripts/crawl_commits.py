import time
import requests
import json
import pdb
import datetime
from config import *

source = "https://github.com/apache?language=java&page="

APACHE_SOURCE = "https://github.com/apache?language=java&page="
APACHE_PROJECT_SOURCE = "https://github.com/apache/"

username = 'intoking'
token = 'd213fcf51e673ba9b6a9bf7b388ffeded21baa2b'
headers = \
            {   'Accept': 'application/vnd.github.cloak-preview', \
                    'Authorization': 'token %s' % token }


def is_recent(item):
    time_string = item["commit"]["author"]["date"][:10]
    date_time = datetime.datetime.strptime(time_string, '%Y-%m-%d')
    # pdb.set_trace()
    return date_time.year >= 2016


if __name__ == '__main__':
    commitfile = open("commits.txt", 'w')

    repofile = open("repo_url.txt", 'r')
    repos = repofile.readlines()
    for repo_url in repos:
        i = 1
        backoff = 2.05
        [org, repo] = repo_url.split('\n')[0].split('/')[-2:]
        if os.path.isfile(f"data/repository_data/{repo}.json"):
            print(f"{PROGRESS}: {repo} is already collected")
            continue
        jsonfile = open("data/repository_data/%s.json" % repo, 'w')
        Items = []
        while True:
            time.sleep(backoff)
            commit_page_link = f"https://api.github.com/search/commits?q=repo:{org}/{repo}/%s+NPE+OR+NullPointerException&page={i}&per_page=100"

            res = requests.get(commit_page_link, auth=(username, token), headers=headers)
            # print("%s request's status : %d, page: %d" % (repo, res.status_code, i))

            if res.status_code == 500 or res.status_code == 404 or res.status_code == 422:
                print(f"{ERROR}: {res.status_code} from {repo}")
                break

            if res.status_code == 429:
                time.sleep(backoff)
                continue

            items = json.loads(res.content.decode("utf-8"))["items"]
            if items == []:
                if i == 0:
                    print(f"{FAIL}: no NPE commits in {repo}")
                break

            recent_items = [item for item in items if is_recent(item)]
            if recent_items == []:
                print(f"{FAIL}: no recent NPE commits from {len(items)} commits in {repo}")
                break

            print(f"{SUCCESS}: {len(recent_items)} commits are collected from {repo}")

            # pdb.set_trace()
            Items += recent_items
            i = i + 1
        jsonfile.write(json.dumps(Items, indent=4))
        jsonfile.flush()
