import glob, shutil, os
import utils
from benchmark_classes import *
from benchmark import *
from config import *
import pdb
import csv
import traceback
import pprint

ROOT_DIR = os.getcwd()
repo_data_list = [Repository.from_json(rp) for rp in glob.glob(f"{ROOT_DIR}/originals/*/repo.json")]
all_commit_urls = [repo_data.commit_url for repo_data in repo_data_list]

all_stored_repos = [Repository.from_json(rp) for rp in glob.glob(f"{ROOT_DIR}/data/target_commits/*.json")]


def get_commit_dict(repo_data: Repository):
    repo = repo_data.repo
    commit_dicts = utils.read_json_from_file(f"{ROOT_DIR}/data/commit_data/{repo}.json")
    for commit_dict in commit_dicts:
        if commit_dict['commit_id'] == repo_data.commit_id:
            return commit_dict

    print(f"cannot find commit_dict from {repo_data.repo}_{repo_data.commit_id}")
    exit(1)


def get_repo_dict(repo_data: Repository):
    repo = repo_data.repo
    repo_dicts = utils.read_json_from_file(f"{ROOT_DIR}/data/repository_data/{repo}.json")
    for repo_dict in repo_dicts:
        if repo_dict['html_url'] == repo_data.commit_url:
            return repo_dict

    print(f"cannot find repo_dict from {repo_data.repo}_{repo_data.commit_id}")
    exit(1)


def is_exact_testfile(file):
    file = os.path.basename(file)
    is_java_file = file.endswith(".java")
    is_test_file = file.startswith("test") or file.startswith("Test") or file.endswith("test.java") or file.endswith(
        "Test.java") or file.endswith("TestCase.java")
    return is_java_file and is_test_file


def has_test_commit(repo_data):
    if any([is_exact_testfile(test_file) for test_file in repo_data.test_files]):
        return True
    else:
        # bug_id = f"{repo_data.repo}_{repo_data.commit_id}"
        # print(f"{FAIL}:no tests in {bug_id}: {repo_data.test_files}")
        return False


def is_npe_msg(commit_msg):
    return "NPE" in commit_msg or "NullPointerException" in commit_msg


def is_npe_commit(commit_dict):
    msg_lines = commit_dict["message"].split("\n")
    if '' in msg_lines:
        msg_lines.remove('')
    return any([is_npe_msg(msg) for msg in msg_lines[:2]])


def is_parent_in(repo_dict):
    parent_urls = [parent["html_url"] for parent in repo_dict["parents"]]
    if len(parent_urls) == 1:
        return False
    return any([parent_url in all_commit_urls for parent_url in parent_urls])


def check_commit(repo_data, commit_dict, repo_dict):
    return repo_data.is_java and repo_data.is_maven and has_test_commit(repo_data) and not is_parent_in(repo_dict)


def is_npe_commit_manual(commit_dict):
    msg = commit_dict["message"]
    print(f"{PROGRESS}: is npe message? {msg}")
    input_value = input()
    if input_value == 'y':
        return True
    elif input_value == 'n':
        return False
    else:
        print(f"{ERROR}: invalid input {input_value}")
        exit(1)


def check_and_store_commit(repo_data):
    commit_dict = get_commit_dict(repo_data)
    repo_dict = get_repo_dict(repo_data)
    bug_id = f"{repo_data.repo}_{repo_data.commit_id}"
    if check_commit(repo_data, commit_dict, repo_dict) is False:
        return

    if os.path.isfile(f"{ROOT_DIR}/data/target_commits/{bug_id}.json") is False and is_npe_commit(commit_dict):
        print(f"{PROGRESS}: {bug_id} is newly added")
        repo_data.to_json(f"{ROOT_DIR}/data/target_commits/{bug_id}.json")
    # elif is_npe_commit_manual(commit_dict):
    #     repo_data.to_json(f"{ROOT_DIR}/data/target_commits/{bug_id}.json")
    else:
        return


def count_commits_to_remove(repo_data):
    bug_id = f"{repo_data.repo}_{repo_data.commit_id}"
    commit_dict = get_commit_dict(repo_data)
    if "Revert" in commit_dict["message"]:
        print(f"{bug_id} is revert commit")


def size_of(bug_id):
    bench_dir = f"{ROOT_DIR}/originals/{bug_id}"
    repo_data = Repository.from_json(f"{bench_dir}/repo.json")
    return repo_data.size


def count():
    not_compiled = []
    cnt_compiled = 0
    cnt_no_npe = 0
    cnt_npe = 0
    all_builds = 0

    repo_data_list = all_stored_repos

    for repo_data in repo_data_list:
        bug_id = f"{repo_data.repo}_{repo_data.commit_id}"
        bench_dir = f"{ROOT_DIR}/benchmarks/{bug_id}"
        if Build.from_json(f"{ROOT_DIR}/originals/{bug_id}/build.json").compiled:
            cnt_compiled += 1
        else:
            not_compiled.append(bug_id)

        if os.path.isfile(f"{bench_dir}/bug.json") is False:
            continue
        all_builds += 1
        bug = Bug.from_json(f"{bench_dir}/bug.json")
        if os.path.isfile(f"{bench_dir}/npe.json"):
            cnt_npe += 1
        elif bug.test_info and bug.test_info.testcases != []:
            cnt_no_npe += 1

    not_compiled = sorted(not_compiled, key=lambda bug_id: size_of(bug_id))
    cnt_repo_dict = {}
    for bug_id in not_compiled:
        repo = bug_id.split("_")[0]
        if repo in cnt_repo_dict:
            cnt_repo_dict[repo] += 1
        else:
            cnt_repo_dict[repo] = 1

    repos = list(cnt_repo_dict.keys())
    for repo in repos:
        if cnt_repo_dict[repo] < 2:
            del cnt_repo_dict[repo]

    # pprint.pprint(f"repo: {cnt_repo_dict}")
    utils.save_dict_to_jsonfile(f"{ROOT_DIR}/to_compile.json", cnt_repo_dict)
    print(f"not compiled : {not_compiled} from {all_builds}")
    print(f"compiled : {cnt_compiled} from {all_builds}")
    print(f"tested: {cnt_no_npe + cnt_npe} from {all_builds}")
    print(f"npe found : {cnt_npe} from {all_builds}")
