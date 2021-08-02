import glob
import os
import json
import subprocess

# root_dir needs a trailing slash (i.e. /root/dir/)
root_dir = os.getcwd() 

for filename in glob.iglob(root_dir + '/benchmark/**/**'):
    last_slash = filename.rfind('/')
    foldername = filename[last_slash+1:]

    minus = foldername.find('-')

    project = foldername[:minus]
    number = foldername[minus+1:]

    with open(filename+"/bug_info.json", "r") as j :
        data = json.load(j)
        
        link = data['git']
        link = link[link.rfind('github.com')+10:link.rfind('.')]

        link = "https://patch-diff.githubusercontent.com/raw" + link + "/pull/" + number + ".diff"
        
        subprocess.call('curl ' + link + ' > ./diff/' + foldername + '.diff', shell=True)
