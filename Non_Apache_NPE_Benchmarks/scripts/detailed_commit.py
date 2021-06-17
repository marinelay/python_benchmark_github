import time
import requests
import json
import pdb
import datetime
import utils
import pprint
from config import *

source = "https://github.com/apache?language=java&page="

APACHE_SOURCE = "https://github.com/apache?language=java&page="
APACHE_PROJECT_SOURCE = "https://github.com/apache/"

username = 'intoking'
token = 'd213fcf51e673ba9b6a9bf7b388ffeded21baa2b'
headers = \
            {   'Accept': 'application/vnd.github.cloak-preview', \
                    'Authorization': 'token %s' % token }

ROOT_DIR = os.getcwd()


def is_exact_testfile(file):
    file = os.path.basename(file)
    is_java_file = file.endswith(".java")
    is_test_file = file.startswith("test") or file.startswith("Test") or file.endswith("test.java") or file.endswith(
        "Test.java") or file.endswith("TestCase.java")
    return is_java_file and is_test_file


def has_test_files(files):
    return any([is_exact_testfile(tf) for tf in files])


def has_java_files(files):
    return any([jf for jf in files if "test" not in jf and jf.endswith(".java")])


def is_npe_msg(commit_msg):
    return "NPE" in commit_msg or "NullPointerException" in commit_msg


def is_npe_commit(commit_dict):
    msg_lines = commit_dict["message"].split("\n")
    if '' in msg_lines:
        msg_lines.remove('')
    return any([is_npe_msg(msg) for msg in msg_lines[:1]])


class generate_bug_data:
    def __init__(self, repo):
        self.repo = repo
        self.jsonfile = utils.read_json_from_file(f"{ROOT_DIR}/data/repository_data/{repo}.json")
        self.repo_commits = self.jsonfile

    def is_done(self):
        return os.path.isfile(f"commit_data/{self.repo}.json")

    def do_repo(self):
        if self.is_done():
            print(f"{PROGRESS}: {self.repo} is already done!")
            return

        outputs = []
        for commit in self.repo_commits:
            data = {}
            data['commit'] = commit['html_url']
            data['repo'] = commit['html_url'].split('/')[-3]
            data['parent'] = commit['parents'][0]['html_url']
            data['message'] = commit['commit']['message']
            data['commit_id'] = commit['html_url'].split('/')[-1][:7]
            data['date'] = commit['commit']['author']['date'][:10]

            bug_id = "%s_%s" % (data['repo'], data['commit_id'])
            [org, repo] = commit['repository']['html_url'].split('/')[-2:]
            commit_hash = commit['html_url'].split('/')[-1]
            data['bug_id'] = bug_id

            link = f'https://api.github.com/repos/{org}/{repo}/commits/{commit_hash}'
            res = requests.get(link, auth=(username, token), headers=headers)

            if len(commit['parents']) != 1:
                print(f"{FAIL}: {bug_id} is merge commit")
                continue

            if is_npe_commit(data) is False:
                print(f"{FAIL}: {bug_id} is not NPE commit")
                continue

            # # End of page
            # if res.status_code == 500 or res.status_code == 404:
            #     continue

            # Should not fail
            if res.status_code == 429:
                print(f"{WARNING}: backoff!, sleep {len(self.repo_commits)} seconds")
                time.sleep(len(self.repo_commits))
                res = requests.get(link, auth=(username, token), headers=headers)

            if res.status_code != 200:
                print(f"{ERROR}: failed to get commit data from {bug_id}")
                print(f"  - status_code : {res.status_code}")
                print(f"  - headers : {res.headers}")
                return

            content = json.loads(res.content.decode("utf-8"))
            data['files'] = []

            if content['files'] == []:
                print(f"{ERROR}: failed to get changed files from %s" % data['commit'])
                exit(1)

            for file in content['files']:
                if 'patch' in file:
                    del file['patch']
                else:
                    print(f"{WARNING}: {bug_id} has no patch data")
                data['files'].append(file)

            changed_files = [d["filename"] for d in data['files']]
            if has_test_files(changed_files) is False or has_java_files(changed_files) is False:
                print(f"{FAIL}: {bug_id} has no TC commit")
                continue

            # pdb.set_trace()
            print(f"{SUCCESS}: {bug_id} has TC commit")
            outputs.append(data)

        if outputs == []:
            print(f"{PROGRESS}: {self.repo} is empty")
            return

        output_file = open(f"{ROOT_DIR}/data/commit_data/{self.repo}.json", 'w')
        output_file.write(json.dumps(outputs, indent=4))
        output_file.flush()
        output_file.close()

        # sleep for limit 5000/hour
        time.sleep(len(self.repo_commits) / 3)
        return


if __name__ == '__main__':
    repos = [os.path.basename(rj)[:-5] for rj in glob.glob(f"{ROOT_DIR}/data/repository_data/*.json")]

    for repo in repos:
        gbd = generate_bug_data(repo.split('\n')[0])
        gbd.do_repo()
