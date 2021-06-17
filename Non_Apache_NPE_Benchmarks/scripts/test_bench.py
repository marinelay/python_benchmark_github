import glob, shutil, os
import utils
from benchmark_classes import *
from benchmark import *
from config import *
import pdb
import traceback

ROOT_DIR = os.getcwd()


def must_execute(cmd, dir):  #should not fail
    ret = utils.execute(cmd, dir=dir)
    if ret.return_code != 0:
        print(f"{ERROR}: failed to execute {cmd} at {dir}")
        exit(1)


def set_java_version(bug: Bug, bug_dir):
    if bug.build_info.java_version == 8:
        java_version = "1.8.0.275"
    elif bug.build_info.java_version == 15:
        java_version = "15.0.1"
    else:
        print(f"{ERROR}: {bug.bug_id}'s java-version is not configured")
        exit(1)

    must_execute(f"jenv local {java_version}", bug_dir)


def is_done(bug: Bug):
    # return False
    return bug.test_info != None


def do_bug(bug: Bug):
    original_dir = f"{ROOT_DIR}/originals/{bug.bug_id}"
    bench_dir = f"{ROOT_DIR}/benchmarks/{bug.bug_id}"

    if is_done(bug):
        return

    test_classes = []
    for test_file in bug.repository_info.test_files:
        if test_file.endswith(".java"):
            test_classes.append(test_file.split(".")[-2].split("/")[-1])

    if test_classes == []:
        print(f"{FAIL}: {bug.bug_id} has no testcases")
        return

    test_cls_opt = ','.join(test_classes)
    test_cmd = f"mvn test -DskipIT -Dtest={test_cls_opt} -DfailIfNoTests=false {MVN_OPTION}"

    ret_compile = utils.execute(f"mvn clean package {MVN_OPTION} {MVN_SKIP_TESTS}", dir=original_dir, timeout=3600)
    if ret_compile.return_code != 0:
        print(f"{ERROR}: {bug.bug_id} is not compiled!!!")
        return

    ret_buggy_test, ret_fixed_test = utils.execute(test_cmd, dir=bench_dir,
                                                   timeout=3600), utils.execute(test_cmd,
                                                                                dir=original_dir,
                                                                                timeout=3600)

    try:
        testcases_buggy, testcases_fixed = TestCase.from_test_results(bench_dir), TestCase.from_test_results(
            original_dir)

    except:
        traceback.print_exc()
        #   print(f"{ERROR}: failed to parse error report for {bug.bug_id}")
        return

    testcases = list(set(testcases_buggy) - set(testcases_fixed))
    if testcases == []:
        print(f"{FAIL} to find testcases of {bug.bug_id}")
    else:
        print(f"{SUCCESS}: to find testcases of {bug.bug_id}")

    bug.test_info = Test(test_command=test_cmd,
                         fail_buggy=ret_buggy_test.return_code == 1,
                         pass_fixed=ret_fixed_test.return_code == 0,
                         testcases=testcases)

    bug.to_json(bench_dir)


all_bug_jsons_path = glob.glob(f"{ROOT_DIR}/benchmarks/*/bug.json")
target_bugs = []
for bug_json_path in all_bug_jsons_path:
    if os.stat(bug_json_path).st_size <= 0:
        print(f"{ERROR}: {bug_json_path} has invalid json")
        os.remove(bug_json_path)
    else:
        bug: Bug = Bug.from_json(bug_json_path)
        if bug.is_buggy_compiled:
            target_bugs.append(bug)

# for target_bug in target_bugs:
#     pdb.set_trace()
#     do_bug(target_bug)
utils.multiprocess(do_bug, target_bugs, n_cpus=10)
