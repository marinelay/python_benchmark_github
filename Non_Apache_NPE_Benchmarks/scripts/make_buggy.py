import glob, shutil, os
import utils
from benchmark_classes import *
from benchmark import *
from config import *
import pdb
import argparse

ROOT_DIR = os.getcwd()

def make_benchmark(repo_data):
    bug_id = f"{repo_data.repo}_{repo_data.commit_id}"
    bench_dir = f"{ROOT_DIR}/benchmarks/{bug_id}"
    parent_id = repo_data.parent_url.split('/')[-1][:7]
    if os.path.isdir(bench_dir):
        shutil.rmtree(bench_dir)

    shutil.copytree(f"{ROOT_DIR}/originals/{bug_id}",
                    bench_dir,
                    dirs_exist_ok=False)
    for patch_file in repo_data.patch_files:
        if utils.execute(f"git checkout {parent_id} -- {patch_file}",
                         bench_dir).return_code != 0:
            print(
                f"{WARNING}: {patch_file} is not checkouted to parent ({bug_id})"
            )

parser = argparse.ArgumentParser()
parser.add_argument("--bug_id", help="bug_id")
args=parser.parse_args()

repo_json_path = f"{ROOT_DIR}/originals/{args.bug_id}/repo.json"
repo_data = Repository.from_json(repo_json_path)

make_benchmark(repo_data)
