import time
import requests
import json
import pdb
import datetime
from config import *

source = "https://github.com/apache?language=java&page="

APACHE_SOURCE = "https://github.com/apache?language=java&page="
APACHE_PROJECT_SOURCE = "https://github.com/apache/"

username = 'intoking'
token = 'd213fcf51e673ba9b6a9bf7b388ffeded21baa2b'
headers = \
            {   'Accept': 'application/vnd.github.cloak-preview', \
                    'Authorization': 'token %s' % token }
            
            
