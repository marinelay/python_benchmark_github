import argparse
from benchmark_classes import *
from typing import List, Set, Dict, Tuple, Optional
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from multiprocessing import Pool
from functools import wraps
import utils
from config import *
import pdb


@dataclass
class Bug:
    bug_id: str
    repository_info: Optional[Repository] = None
    build_info: Optional[Build] = None
    test_info: Optional[Test] = None
    npe_info: List[Npe] = field(default_factory=list)
    patch_results: List[Patch] = field(default_factory=list)
    is_buggy_compiled: Optional[bool] = None

    @classmethod
    def from_json(cls, jsonfile):
        bug = from_dict(cls, utils.read_json_from_file(jsonfile))
        if bug.npe_info is None:
            bug.npe_info = []
        if bug.patch_results is None:
            bug.patch_results = []
        return bug

    @classmethod
    def from_branch(cls, target_branch):
        bug_dir = f"{ROOT_DIR}/{target_branch}"
        return cls.from_json(f"{bug_dir}/bug.json")

    def to_json(self, dir):
        utils.save_dict_to_jsonfile(f"{dir}/bug.json", asdict(self))

    def checkout(self, dir):
        execute(f"git checkout -f benchmarks/{self.bug_id}", dir)
        metadata_list = [
            "bug.json", "patches", "infer-out", "trace.json", "npe*.json"
        ]
        excludes = ' '.join(
            [f"--exclude={metadata}" for metadata in metadata_list])
        execute(f"git clean -df {excludes}", dir)

    def execute_compile(self, dir):
        java_version = self.build_info.java_version
        compile_cmd = utils.get_compile_command(dir, java_version=java_version)
        return utils.execute(
            compile_cmd,
            dir=dir,
            env=utils.set_java_version(java_version=java_version))

    def execute_test(self, dir, verbosity=0, env=os.environ):
        test_cmd = f'mvn clean test -DfailIfNoTests=false {MVN_OPTION}' + f" -Dtest={self.test_info.testcases[0].classname}#{self.test_info.testcases[0].method}"
        # test_cmd = f'mvn clean test -DfailIfNoTests=false {MVN_OPTION}'
        # for testcase in self.test_info.testcases:
        #     test_cmd = test_cmd + f" -Dtest={testcase.classname}#{testcase.method}"

        if "_JAVA_OPTIONS" not in env:
            env = utils.set_java_version(
                java_version=self.build_info.java_version)

        self.test_info.test_command = test_cmd
        return utils.execute(test_cmd, dir=dir, env=env, verbosity=verbosity)

    # ### Steps to construct benchmarks: build, test, generate patch, validate ...
    # def build_info(self, dir):
    #     for java_version in [8, 7, 11]:
    #         compile_cmd = utils.get_compile_command(dir, java_version=java_version)
    #         ret_compile = utils.execute(compile_cmd, dir=dir, env=utils.set_java_version(java_version=java_version))
    #         if ret_compile.return_code == 0:
    #             self.build_info = Build(compiled=True,
    #                                     build_command=compile_cmd,
    #                                     java_version=java_version,
    #                                     time=ret_compile.time)
    #             print(f"{SUCCESS}: successfully compiled {self.bug_id} by java {java_version}")
    #             break
    #         else:
    #             continue

    #     if ret_compile.return_code != 0:
    #         print(f"{FAIL}: failed to compile {self.bug_id}")
    #         self.build_info = Build(compiled=False, error_message=utils.parse_error(ret_compile.stdout))

    # def test_info(self, dir):
    #     def execute_test_all(self, dir):
    #         java_version = self.build_info.java_version
    #         if self.repository_info:
    #             test_classes = [os.path.basename(file).split('.')[-2] for file in self.repository_info.test_files]
    #         else:
    #             test_classes = []

    #         test_cmd = utils.get_test_command(dir, java_version=java_version, test_classes=test_classes)
    #         return utils.execute(test_cmd, dir=dir, env=utils.set_java_version(java_version=java_version))

    #     if not self.build_info or self.build_info.compiled is False:
    #         print(f"{WARNING}: {self.bug_id} is not compiled")
    #         return

    #     test_cmd = utils.get_test_command(dir, java_version=self.build_info.java_version)

    #     fixed_branch = self.bug_id.rstrip("-buggy")
    #     execute(f"git checkout benchmarks/{fixed_branch}", dir)
    #     ret_fixed_test = self.execute_test_all(dir)
    #     testcases_fixed = TestCase.from_test_results(dir)

    #     execute(f"git checkout benchmarks/{self.bug_id}", dir)
    #     ret_buggy_test = self.execute_test_all(dir)
    #     testcases_buggy = TestCase.from_test_results(dir)

    #     testcases = list(set(testcases_buggy) - set(testcases_fixed))

    #     if testcases != []:
    #         print(f"{SUCCESS}: found validating testcases for {self.bug_id}")
    #     else:
    #         print(f"{FAIL}: failed to find meaningful testcases for {self.bug_id}")

    #     self.test_info = Test(test_command=test_cmd,
    #                           fail_buggy=ret_buggy_test.return_code == 1,
    #                           pass_fixed=ret_fixed_test.return_code == 0,
    #                           testcases=testcases)

    def patch(self, dir):
        self.patch_results = []
        self.checkout(dir)

        ### Pre condition ###
        if os.path.isdir(f"{dir}/patches"):
            execute(f"rm -rf {dir}/patches", dir)

        for npe in self.npe_info:
            utils.save_dict_to_jsonfile(f"{dir}/npe.json", asdict(npe))
            env = utils.set_java_version(self.build_info.java_version)
            utils.execute(
                f"java -cp {SYNTHESIZER} npex.synthesizer.Main -patch {dir} {dir}/npe.json"
            )
            patch_dirs = glob.glob(f"{dir}/patches/*")
            for patch_dir in patch_dirs:
                patch_id = os.path.basename(patch_dir)
                if os.path.isfile(f"{patch_dir}/patch.json") is False:
                    execute(f"rm -rf {patch_dir}", dir)
                    print(f"{ERROR} {self.bug_id}-{patch_id} NOT IMPLEMENTED")
                    continue
                original_filepath = utils.read_json_from_file(
                    f"{patch_dir}/patch.json")["original_filepath"]
                self.patch_results.append(
                    Patch(patch_id=patch_id,
                          patch_dir=patch_dir,
                          original_filepath=original_filepath))

        ### Print ###
            if self.patch_results != []:
                print(
                    f"{PROGRESS}: {len(self.patch_results)} patches are generated for {self.bug_id}"
                )
            else:
                print(f"{SERIOUS}: no patches are generated for {self.bug_id}")

    def validate_patch(self, dir):
        for patch in self.patch_results:
            if patch.compiled is False or patch.pass_testcase is not None:
                continue
            self.checkout(dir)
            execute(
                f"cp \"{patch.patch_dir}/patch.java\" {dir}/{patch.original_filepath}",
                dir)
            patch.compiled = self.execute_compile(dir).return_code == 0
            if patch.compiled and self.test_info.testcases != []:
                patch.pass_testcase = self.execute_test(dir).return_code == 0

    def generate_trace(self, dir):
        self.checkout(dir)
        if os.path.isfile(f"{dir}/trace.json"):
            execute(f"rm trace.json", dir=dir)

        if self.test_info == None:
            print(f"{WARNING}: {self.bug_id} has no test_info")
            return False

        if self.test_info.testcases == []:
            print(f"{WARNING}: {self.bug_id} has no testcases")
            return False

        env = deepcopy(os.environ)
        if self.build_info.java_version == 8 or self.build_info.java_version == 11:
            env["_JAVA_OPTIONS"] = f"-javaagent:{TRACER8}={dir},{self.test_info.testcases[0].classname}#{self.test_info.testcases[0].method}"
        elif self.build_info.java_version == 7:
            print(f"{WARNING}: not supported java version for {self.bug_id}")
            return False
            # env["_JAVA_OPTIONS"]= f"-javaagent:{TRACER7}={dir}"
        else:
            print(f"{WARNING}: not supported java version for {self.bug_id}")
            return False

        ret_test = self.execute_test(dir, env=env)
        f = open(f"{dir}/1", 'w')
        f.write(ret_test.stdout)
        f.close()
        self.checkout(dir)
        return TraceEntry.generate_trace_json(ret_test.stdout.split('\n'), dir)

    @staticmethod
    def configure(target_branch):
        print(f"{PROGRESS}: configuring {target_branch}...")
        bug_dir = f"{ROOT_DIR}/{target_branch}"

        if os.path.isdir(bug_dir) is False:
            utils.execute(f"cp -r {SEED_DIR} {bug_dir}",
                          dir=ROOT_DIR,
                          verbosity=1)
            execute(f"git checkout benchmarks/{target_branch}", dir=bug_dir)

        if os.path.isfile(f"{bug_dir}/bug.json"):
            bug = Bug.from_json(f"{bug_dir}/bug.json")
        else:
            bug = Bug(target_branch)

        bug.checkout(bug_dir)

        if bug.build_info is None:
            bug.build_info(bug_dir)

        if bug.test_info is None or bug.test_info.testcases == []:
            bug.test_info(bug_dir)
