import sqlite3
import subprocess
import os
import requests
from getpass import getpass

DB = "students_db.db"

if __name__ == "__main__":

    username = 'pyneng'
    password = os.environ.get('GITHUB_PASS')
    if not password:
        password = getpass('Пароль для моего акаунта pyneng')

    conn = sqlite3.connect(DB)
    query = 'select repo_name from students'
    for row in conn.execute(query):
        repo_name = row[0]
        subprocess.run(
            f'git clone ssh://git@github.com/pyneng/{repo_name}.git', shell=True)
        print(repo_name)

