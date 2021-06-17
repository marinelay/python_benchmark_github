import os, sys, glob
import time
import argparse
import re
import requests
from bs4 import BeautifulSoup
from easyprocess import EasyProcess
from multiprocessing import Process
from multiprocessing import Pool
from functools import partial

source = "https://github.com/apache?language=java&page="

if __name__ == '__main__':
    i = 1
    repos = []
    logfile = open("repo.txt", 'a')
    while True: 
        res = requests.get(source + str(i))
        if res.status_code == 500:
            break
           
        if res.status_code == 429:
            time.sleep(1)
            continue
        
        soup = BeautifulSoup(res.content, 'html.parser')
        
        h3s = soup.find_all('h3')[1:]

        links = [data.contents[1]['href'] for data in h3s]
        repos = repos + [link.split('/').pop() for link in links]
        print(str(i) + " page done: " + str(res.status_code))
        i = i + 1

    repo_names = '\n'.join(repos)
    logfile.writelines(repo_names)



