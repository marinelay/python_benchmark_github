import sys
import getopt
import json
import os

def main(argv) :
    FILE_NAME     = argv[0] # command line arguments의 첫번째는 파일명
    PROJECT_NAME = ""      # 인스턴스명 초기화

    try:
        # opts: getopt 옵션에 따라 파싱 ex) [('-i', 'myinstancce1')]
        # etc_args: getopt 옵션 이외에 입력된 일반 Argument
        # argv 첫번째(index:0)는 파일명, 두번째(index:1)부터 Arguments
        opts, etc_args = getopt.getopt(argv[1:], \
                                 "n:", ["name="])

    except getopt.GetoptError: # 옵션지정이 올바르지 않은 경우
        print(FILE_NAME, '-n <project name>')
        sys.exit(2)

    for opt, arg in opts: # 옵션이 파싱된 경우
        if opt in ("-n", "--name"): # HELP 요청인 경우 사용법 출력
            PROJECT_NAME = arg

    if len(PROJECT_NAME) < 1: # 필수항목 값이 비어있다면
        print(FILE_NAME, "-n option is mandatory") # 필수임을 출력
        sys.exit(2)

    with open("benchmark.json", "r") as pj_json :
        pj_dict = json.load(pj_json)

    os.system("chmod +x benchmark.sh")

    for pj, values in pj_dict.items() :
        if pj == PROJECT_NAME :
            for value, py_version in values.items() :
                
                os.system("./benchmark.sh " + value + " " + py_version)

if __name__ == "__main__":
    main(sys.argv)