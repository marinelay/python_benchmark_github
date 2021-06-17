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
    return os.path.isfile(f"{ROOT_DIR}/benchmarks/{bug.bug_id}/npe.json")
    # return bug.test_info != None


def do_bug(bug: Bug):
    bench_dir = f"{ROOT_DIR}/benchmarks/{bug.bug_id}"

    if is_done(bug):
        print(f"{PROGRESS}: {bug.bug_id} is already done")
        return

    test_cls = bug.test_info.testcases[0].classname
    test_mthd = bug.test_info.testcases[0].method.split("{")[0]
    test_cmd = f"mvn test -DskipIT -Dtest={test_cls}#{test_mthd} -DfailIfNoTests=false {MVN_OPTION}"

    print(f"{PROGRESS}: testing {bug.bug_id}...")
    utils.set_detailed_npe(bug.build_info.java_version)
    utils.execute(test_cmd, dir=bench_dir, timeout=3600)

    if os.path.isfile(f"{bench_dir}/npe.json"):
        print(f"{SUCCESS}: to find npe.json")
    else:
        print(f"{FAIL}: to find npe.json")


all_bug_jsons_path = glob.glob(f"{ROOT_DIR}/benchmarks/*/bug.json")
target_bugs = []
for bug_json_path in all_bug_jsons_path:
    if os.stat(bug_json_path).st_size <= 0:
        print(f"{ERROR}: {bug_json_path} has invalid json")
        os.remove(bug_json_path)
    else:
        bug: Bug = Bug.from_json(bug_json_path)
        if bug.test_info and bug.test_info.testcases != []:
            target_bugs.append(bug)

# for target_bug in target_bugs:
#     pdb.set_trace()
#     do_bug(target_bug)
utils.multiprocess(do_bug, target_bugs, n_cpus=11)
