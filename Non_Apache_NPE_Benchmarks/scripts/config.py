import json
import time
import os, sys, glob
import re
import subprocess

from typing import List, Set, Dict, Tuple, Optional
import xml.etree.ElementTree as ET
from colorama import Fore, Style  #type:ignore

MVN_OLD = "/home/junhee/tools/apache-maven-3.2.5/bin/mvn"
MVN_OPTION = "-V -B -Denforcer.skip=true -Dcheckstyle.skip=true -Dcobertura.skip=true -Drat.skip=true -Dlicense.skip=true -Dfindbugs.skip=true -Dgpg.skip=true -Dskip.npm=true -Dskip.gulp=true -Dskip.bower=true -Drat.numUnapprovedLicenses=100"
MVN_SKIP_TESTS = "-DskipTests=true -DskipITs=true -Dtest=None -DfailIfNoTests=false"
INFER = "/home/junhee/projects/npex-analyzer-1.0/infer/bin/infer"

ERROR = f"{Fore.RED}[ERROR]{Style.RESET_ALL}"
FAIL = f"{Fore.YELLOW}[FAIL]{Style.RESET_ALL}"
WARNING = f"{Fore.MAGENTA}[WARNING]{Style.RESET_ALL}"
SUCCESS = f"{Fore.CYAN}[SUCCESS]{Style.RESET_ALL}"
TIMEOUT = f"{Fore.LIGHTMAGENTA_EX}[TIMEOUT]{Style.RESET_ALL}"
PROGRESS = f"{Fore.LIGHTWHITE_EX}[PROGRESS]{Style.RESET_ALL}"
SERIOUS = f"{Fore.LIGHTRED_EX}[SERIOUS]{Style.RESET_ALL}"

JDK_6 = "/usr/lib/jvm/jdk1.6.0_45"
JDK_7 = "/usr/lib/jvm/jdk1.7.0_80"
JDK_8 = "/usr/lib/jvm/java-8-openjdk-amd64"
JDK_11 = "/usr/lib/jvm/jdk-11.0.8"

DETAILED_NPE6 = "-agentpath:/home/june/project/detailedNPE/detailedNPE_6.so"
DETAILED_NPE7 = "-agentpath:/home/june/project/detailedNPE/detailedNPE_7.so"
DETAILED_NPE8 = "-agentpath:/home/june/project/detailedNPE/detailedNPE_8.so"
DETAILED_NPE11 = "-agentpath:/home/june/project/detailedNPE/detailedNPE_11.so"
DETAILED_NPE13 = "-agentpath:/home/june/project/detailedNPE/detailedNPE_13.so"
DETAILED_NPE15 = "-agentpath:/home/june/project/detailedNPE/detailedNPE_15.so"

SYNTHESIZER = "/home/junhee/projects/npex/synthesizer/target/synthesizer-1.0-SNAPSHOT-jar-with-dependencies.jar"
TRACER = "/home/june/project/npex/errortracer/target/instrumentation-jar-with-dependencies.jar"
TRACER7 = "/home/junhee/projects/npex/tracer7.jar"
TRACER8 = "/home/junhee/projects/npex/tracer8.jar"

MSG_TEST_FAIL = "test failures"
MSG_ASSERT_FAIL = "Assertion"
MSG_COMPILE_FAIL = "Compilation failure"
MSG_NPE = "NullPointerException"

BECHMARKS_DIR = '/media/4tb/npex/npex_data/benchmarks'
LEARNING_DATA_DIR = '/media/4tb/npex/npex_data/learningData'

'''
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s/%(levelname)s]%(processName)s - %(message)s')
file_handler = logging.FileHandler("logs/check_NPE.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
'''
