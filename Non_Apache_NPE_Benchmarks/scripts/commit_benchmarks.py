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


def is_done(bug: Bug):
    # pdb.set_trace()
    bench_dir = f"{ROOT_DIR}/benchmarks/{bug.bug_id}"
    giturl = "https://github.com/kupl/Non_Apache_NPE_Benchmarks.git"
    return giturl in utils.execute("git config --get remote.origin.url", bench_dir).stdout
    # return False


def do_bug(bug: Bug):
    # pdb.set_trace()
    if is_done(bug):
        print(f"{PROGRESS}: {bug.bug_id} is already done")
        return

    bench_dir = f"{ROOT_DIR}/benchmarks/{bug.bug_id}"

    must_execute(f"mvn clean", bench_dir)
    must_execute(f"rm -rf {bench_dir}/.git*", bench_dir)
    must_execute(f"cp -r {ROOT_DIR}/.git {bench_dir}/", bench_dir)
    must_execute(f"git checkout -b {bug.bug_id}", bench_dir)
    must_execute(f"git add -A", bench_dir)
    must_execute(f"git commit -m \"add {bug.bug_id}\"", bench_dir)
    utils.execute(f"git push --set-upstream origin {bug.bug_id}", dir=bench_dir, verbosity=1)


all_bug_jsons_path = glob.glob(f"{ROOT_DIR}/benchmarks/*/bug.json")
target_bugs = []
for bug_json_path in all_bug_jsons_path:
    if os.stat(bug_json_path).st_size <= 0:
        print(f"{ERROR}: {bug_json_path} has invalid json")
        os.remove(bug_json_path)
    else:
        bug: Bug = Bug.from_json(bug_json_path)
        bug_dir = f"{ROOT_DIR}/benchmarks/{bug.bug_id}"
        if bug.test_info and bug.test_info.testcases != [] and os.path.isfile(f"{bug_dir}/npe.json"):
            target_bugs.append(bug)

# for target_bug in target_bugs:
#     # pdb.set_trace()
#     do_bug(target_bug)
utils.multiprocess(do_bug, target_bugs, n_cpus=10)
