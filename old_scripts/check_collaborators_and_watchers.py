import os
import sqlite3
import time
from getpass import getpass

import requests


DB = "students_db.db"

username = 'pyneng'
password = os.environ.get('GITHUB_PASS')
if not password:
    password = getpass('Пароль для акаунта pyneng')


conn = sqlite3.connect(DB)
query = 'select repo_name, student from students'
all_repos = sorted([data[0] for data in conn.execute(query)])

conn.close()

print('#'*20, 'Всего репозиториев:', len(all_repos))

#### Collaborators
def check_collaborators():
    link = 'https://api.github.com/repos/pyneng/{}/collaborators'

    collaborators_done = [
    ]

    to_check_collaborators = sorted(set(all_repos) - set(collaborators_done))
    new_collaborators_done = []

    for repo in to_check_collaborators:
        rep_coll = requests.get(link.format(repo), auth=(username, password))
        if len(rep_coll.json()) == 2:
            new_collaborators_done.append(repo)
        time.sleep(5)

    print("Слушатели добавились как collaborator")
    print('\n'.join(new_collaborators_done))
    print(new_collaborators_done)

    print('#'*60)
    not_done = sorted(set(all_repos) - set(collaborators_done) - set(new_collaborators_done))
    print("Осталось {} слушателей, которые НЕ добавились как collaborator".format(
        len(not_done)))
    print('\n'.join(not_done))

def check_watchers():
    link = 'https://api.github.com/repos/pyneng/{}/subscribers'
    watchers_done = [
                    ]
    to_check_watchers = sorted(set(all_repos) - set(watchers_done))
    new_watchers_done = []

    for repo in to_check_watchers:
        rep_sub = requests.get(link.format(repo), auth=(username, password))
        response_json = rep_sub.json()
        if len(response_json) == 2:
            new_watchers_done.append(repo)
        elif len(response_json) == 0:
            print('забыла нажать watch', repo)
        #print('#'*20, repo)
        #for sub in response_json:
        #    print(sub['login'])
        time.sleep(5)

    print("Слушатели добавились как watchers")
    print('\n'.join(new_watchers_done))
    print(new_watchers_done)

    print('#'*60)
    not_done = list(set(all_repos) - set(watchers_done) - set(new_watchers_done))
    print("{} слушателей НЕ нажали watch".format(len(not_done)))
    print('\n'.join(sorted(not_done)))



if __name__ == "__main__":
    check_collaborators()
    check_watchers()

