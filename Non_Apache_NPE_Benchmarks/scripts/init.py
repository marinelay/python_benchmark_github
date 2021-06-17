import glob, shutil, os
import utils
from benchmark_classes import *
from benchmark import *
from config import *
import pdb

ROOT_DIR = os.getcwd()


def must_execute(cmd, dir):  #should not fail
    ret = utils.execute(cmd, dir=dir)
    if ret.return_code != 0:
        print(f"{ERROR}: failed to execute {cmd} at {dir}")
        exit(1)


def do_branch(branch):
    bench_dir = f"{ROOT_DIR}/benchmarks/{branch}"
    os.makedirs(bench_dir, exist_ok=True)
    if os.path.isdir(f"{bench_dir}/.git") is False:
        must_execute(f"cp -r {ROOT_DIR}/.git {bench_dir}/.git", bench_dir)
    must_execute(f"git checkout -f {branch}", bench_dir)


all_branches = utils.execute("git branch -a", dir=ROOT_DIR).stdout.splitlines()
target_branches = [branch.strip('\n').split("/")[-1] for branch in all_branches if "_" in branch]

# for target_bug in target_bugs:
#     # pdb.set_trace()
#     do_bug(target_bug)
utils.multiprocess(do_branch, target_branches, n_cpus=10)
