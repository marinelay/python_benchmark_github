import glob, shutil, os
import utils
from benchmark_classes import *
from benchmark import *
from config import *
import pdb
import csv
import traceback

ROOT_DIR = os.getcwd()


def must_execute(cmd, dir):  #should not fail
    ret = utils.execute(cmd, dir=dir)
    if ret.return_code != 0:
        print(f"{ERROR}: failed to execute {cmd} at {dir}")
        exit(1)


def do_bug(bug):
    bench_dir = f"{ROOT_DIR}/benchmarks/{bug.bug_id}"
    bug = Bug.from_json(f"{bench_dir}/bug.json")
    npe_dict = utils.read_json_from_file(f"{bench_dir}/npe.json")
    return [bug.bug_id, bug.repository_info.commit_url, npe_dict["filepath"], npe_dict["line"]]


all_branches = utils.execute("git branch -a", dir=ROOT_DIR).stdout.splitlines()
target_branches = [branch.strip('\n').split("/")[-1] for branch in all_branches if "_" in branch]

target_bugs = []
for branch in target_branches:
    bench_dir = f"{ROOT_DIR}/benchmarks/{branch}"
    if os.path.isfile(f"{bench_dir}/npe.json"):
        target_bugs.append(Bug.from_json(f"{bench_dir}/bug.json"))


def remove_branch(bug: Bug):
    bench_dir = f"{ROOT_DIR}/benchmarks/{bug.bug_id}"
    if os.path.isfile(f"{ROOT_DIR}/data/target_commits/{bug.bug_id}.json"):
        return

    print(f"{bench_dir} is not target")
    utils.execute(f"rm .git/refs/remotes/origin/{bug.bug_id}", ROOT_DIR, verbosity=1)
    # utils.execute(f"git branch -d {bug.bug_id}", ROOT_DIR, verbosity=1)
    # utils.execute(f"git push origin --delete {bug.bug_id}", ROOT_DIR, verbosity=1)


csvfile = open("study.csv", 'w', newline="\n")
writer = csv.writer(csvfile, delimiter=' ')
writer.writerow(["Id", "Commits", "NPE-path", "NPE-line"])
# for bug in target_bugs:
#     remove_branch(bug)
rows = utils.multiprocess(do_bug, target_bugs, n_cpus=10)
writer.writerows(rows)
csvfile.close()
