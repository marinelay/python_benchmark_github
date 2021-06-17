import glob, shutil, os
import utils
from benchmark_classes import *
from config import *
import pdb

ROOT_DIR = os.getcwd()


def is_done(dir_to_store):
    return os.path.isfile(f"{dir_to_store}/repo.json")


def do_commit(repo_data: Repository):
    bug_id = f"{repo_data.repo}_{repo_data.commit_id}"
    dir_to_store = f"{ROOT_DIR}/originals/{bug_id}"

    if is_done(dir_to_store):
        print(f"{PROGRESS}: {bug_id} is done")
        return

    clone_cmd = f"git clone {repo_data.repo_url} {dir_to_store}"
    checkout_cmd = f"git checkout -f {repo_data.commit_id}"
    if os.path.isdir(dir_to_store):
        shutil.rmtree(dir_to_store)
    ret_clone = utils.execute(clone_cmd, ROOT_DIR)
    ret_checkout = utils.execute(checkout_cmd, dir_to_store)
    # pdb.set_trace()
    if ret_checkout.return_code == 0 and ret_clone.return_code == 0:
        if os.path.isfile(f"{dir_to_store}/pom.xml"):
            print(f"{SUCCESS}: clone and checkout maven project for {bug_id}")
            repo_data.is_maven = True
            repo_data.size = utils.size_of(dir_to_store)
        else:
            print(f"{FAIL}: {bug_id} is not maven project")
            repo_data.is_maven = False

        repo_data.to_json(f"{dir_to_store}/repo.json")
    else:
        print(f"{ERROR}: occurs during clone and checkout {bug_id}")


commit_data_json_paths = glob.glob(f"{ROOT_DIR}/data/commit_data/*.json")
repo_data_list = []
for jp in commit_data_json_paths:
    for repo_data_dict in utils.read_json_from_file(jp):
        repo_data_list.append(Repository.from_commit_data(repo_data_dict))

# do_commit(repo_data_list[0])
utils.multiprocess(do_commit, repo_data_list, n_cpus=10)
