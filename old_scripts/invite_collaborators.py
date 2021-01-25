import sqlite3
import time
import os
from getpass import getpass

import requests


DB = 'students_db.db'

username = 'pyneng'
password = os.environ.get('GITHUB_PASS')
if not password:
    password = getpass('Пароль для моего акаунта pyneng')


link = 'https://api.github.com/repos/pyneng/{}/collaborators/{}?permission=none'


conn = sqlite3.connect(DB)
query = 'select repo_name, github from students'
for row in conn.execute(query):
    repo, user = row
    resp = requests.put(link.format(repo, user), auth=(username, password))
    if resp.status_code == 201:
        print('OK', repo)
    else:
        print('NOT OK', repo)
    time.sleep(5)

