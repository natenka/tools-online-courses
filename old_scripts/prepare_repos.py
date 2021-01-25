import subprocess
import time
import sqlite3
import os
import requests
from getpass import getpass
import json
from transliterate import translit
from pprint import pprint


create_template = {
    "has_issues": False,
    "has_projects": False,
    "has_wiki": False,
    "name": None,
    "private": True,
    "default_branch": "main",
}

DB = "students_db.db"


def invite_collaborators():
    username = 'pyneng'
    password = os.environ.get('GITHUB_PASS')
    if not password:
        password = getpass('Пароль для моего акаунта pyneng')


    api_link = 'https://api.github.com/repos/pyneng/{}/collaborators/{}?permission=none'

    conn = sqlite3.connect(DB)
    query = 'select repo_name, github from students'
    for row in conn.execute(query):
        repo, user = row
        resp = requests.put(api.format(repo, user), auth=(username, password))
        if resp.status_code == 201:
            print('OK', repo)
        else:
            print('NOT OK', repo)
        time.sleep(5)


def clone_repos():
    conn = sqlite3.connect(DB)
    query = 'select repo_name from students'
    for row in conn.execute(query):
        repo_name = row[0]
        subprocess.run(
            f'git clone ssh://git@github.com/pyneng/{repo_name}.git', shell=True)
        print(repo_name)


def create_email_repo_map():
    repos = {}
    conn = sqlite3.connect("students_db.db")
    conn.row_factory = sqlite3.Row
    all_students = "select email, student from students order by student"

    for st in conn.execute(all_students):
        st_name = st["student"]
        st_email = st["email"]
        st_name_translit = translit(st_name.strip().lower(), "ru", reversed=True)
        repo_name = f"online-10-{st_name_translit.replace(' ', '-')}"
        repos[st_email] = repo_name.replace("j", "y").replace("'", "")
    return repos


repos_done = {}


def add_repo_to_db(repos):
    failed_to_create = {}

    conn = sqlite3.connect("students_db.db")
    set_repo_name_query = "update students set repo_name = ? where email = ?"
    for email, repo_name in repos.items():
        conn.execute(set_repo_name_query, (repo_name, email))
    conn.commit()


def create_repos(repos):
    """
    Перейти на pygithub

    g = Github(token)
    user = g.get_user()
    repo = user.create_repo(**create_template)
    """
    failed_to_create = {}
    username = "pyneng"
    password = os.environ.get("GITHUB_PASS")
    if not password:
        password = getpass("Пароль для моего акаунта pyneng")

    conn = sqlite3.connect("students_db.db")
    get_st_by_email = "select * from students where email = ?"
    for email, repo_name in repos.items():
        create_template["name"] = repo_name
        resp = requests.post(
            "https://api.github.com/user/repos",
            data=json.dumps(create_template),
            auth=(username, password),
        )
        if resp.status_code == 201:
            print("################ OK", repo_name)
        else:
            failed_to_create[email] = repo_name
        time.sleep(3)
    conn.commit()
    conn.close()
    if failed_to_create:
        print("### не получилось создать репозиторий")
        pprint(failed_to_create)


if __name__ == "__main__":
    repos_all = create_email_repo_map()
    # for email, repo in repos_all.items():
    #    print(f"{email:35} {repo}")
    create_repos(repos_all)
    add_repo_to_db(repos_all)
