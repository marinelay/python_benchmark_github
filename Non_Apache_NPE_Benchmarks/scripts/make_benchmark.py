import glob, shutil, os
import utils
from benchmark_classes import *
from benchmark import *
from config import *
import pdb

ROOT_DIR = os.getcwd()
COMPILE_CMD = f"mvn clean package {MVN_OPTION} {MVN_SKIP_TESTS}"


def must_execute(cmd, dir):  #should not fail
    ret = utils.execute(cmd, dir=dir)
    if ret.return_code != 0:
        print(f"{ERROR}: failed to execute {cmd} at {dir}")
        exit(1)


def set_java_version(dir, version):
    must_execute(f"jenv local {version}", dir)


def configure_java_version(dir):
    # try compile by 15
    print(f"{PROGRESS}: try to compile {os.path.basename(dir)} by java15")
    set_java_version(dir, "15.0.1")
    ret_compile_15 = utils.execute(COMPILE_CMD, dir=dir)
    if ret_compile_15.return_code == 0:
        return Build(compiled=True, java_version=15)

    # try compile by 13
    print(f"{PROGRESS}: try to compile {os.path.basename(dir)} by java13")
    set_java_version(dir, "13.0.2")
    ret_compile_15 = utils.execute(COMPILE_CMD, dir=dir)
    if ret_compile_15.return_code == 0:
        return Build(compiled=True, java_version=13)

    # try compile by 11
    print(f"{PROGRESS}: try to compile {os.path.basename(dir)} by java11")
    set_java_version(dir, "11.0.8")
    ret_compile_15 = utils.execute(COMPILE_CMD, dir=dir)
    if ret_compile_15.return_code == 0:
        return Build(compiled=True, java_version=11)

    # try compile by 8
    print(f"{PROGRESS}: try to compile {os.path.basename(dir)} by java8")
    set_java_version(dir, "1.8.0.275")
    ret_compile_8 = utils.execute(COMPILE_CMD, dir=dir)
    if ret_compile_8.return_code == 0:
        return Build(compiled=True, java_version=8)

    # try compile by 7
    print(f"{PROGRESS}: try to compile {os.path.basename(dir)} by java7")
    set_java_version(dir, "1.7.0.80")
    ret_compile_8 = utils.execute(COMPILE_CMD, dir=dir)
    if ret_compile_8.return_code == 0:
        return Build(compiled=True, java_version=7)

    else:
        # java_15_msg = f"\n======= Java 15 msg =======\n{ret_compile_15.stdout}"
        # java_8_msg = f"\n======= Java 8 msg ========\n{ret_compile_8.stdout}"
        # return Build(compiled=False, error_message=java_15_msg + java_8_msg)
        return Build(compiled=False)


def make_and_compile_benchmark(repo_data):
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
    # patch_files = ' '.join(repo_data.patch_files)
    # must_execute(f"git checkout {parent_id} -- {patch_files}", bench_dir)
    return utils.execute(COMPILE_CMD, dir=bench_dir).return_code == 0


def do_repo(repo_data):
    bug_id = f"{repo_data.repo}_{repo_data.commit_id}"
    repo_dir = f"{ROOT_DIR}/originals/{bug_id}"
    bench_dir = f"{ROOT_DIR}/benchmarks/{bug_id}"

    if os.path.isfile(f"{repo_dir}/build.json"):
        build_info = Build.from_json(f"{repo_dir}/build.json")
    else:
        build_info = configure_java_version(repo_dir)
        build_info.to_json(repo_dir)

    if build_info.compiled is False:
        print(f"{FAIL}: to compile original {bug_id}")
        return

    print(f"{PROGRESS}: try make buggy from {bug_id}")
    if os.path.isfile(f"{bench_dir}/bug.json") and os.stat(
            f"{bench_dir}/bug.json").st_size > 0 and Bug.from_json(
                f"{bench_dir}/bug.json").is_buggy_compiled:
        bug = Bug.from_json(f"{bench_dir}/bug.json")
    else:
        bug = Bug(bug_id)
        bug.is_buggy_compiled = make_and_compile_benchmark(repo_data)

    bug.build_info = build_info
    bug.repository_info = repo_data

    if bug.is_buggy_compiled is False:
        print(f"{FAIL} to compile buggy-version of {bug_id}")
    else:
        print(f"{SUCCESS}: to compile buggy {bug_id}")

    bug.to_json(bench_dir)


all_repo_json_paths = glob.glob(f"{ROOT_DIR}/originals/*/repo.json")
all_repo_data = [Repository.from_json(jp) for jp in all_repo_json_paths]

target_repos = [rd for rd in all_repo_data if rd.is_maven and rd.is_java]
# for target_repo in target_repos:
#     do_repo(target_repo)
utils.multiprocess(do_repo, target_repos, n_cpus=10)
