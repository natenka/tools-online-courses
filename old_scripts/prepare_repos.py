import subprocess
import github
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
}

DB = "students_db.db"


def call_command(command, verbose=True):
    """
    Функция вызывает указанную command через subprocess
    и выводит stdout и stderr, если флан verbose=True.
    """
    result = subprocess.run(
        command,
        shell=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )
    stdout = result.stdout
    if verbose:
        print("#" * 20, command)
        if stdout:
            print(stdout)
    return stdout


def invite_collab_to_repo(github_obj, repo, collaborator):
    repo_name = f"pyneng/{repo}"

    try:
        repo_obj = github_obj.get_repo(repo_name)
    except github.GithubException:
        raise ValueError(
            "Аутентификация по токену не прошла"
        )
    else:
        repo_obj.add_to_collaborators(collaborator)


def invite_collaborators():
    token = os.environ.get("GITHUB_TOKEN")
    github_obj = github.Github(token)

    conn = sqlite3.connect(DB)
    query = 'select repo_name, github from students'
    for repo, user in conn.execute(query):
        if user:
            invite_collab_to_repo(g, repo, user)
            time.sleep(2)
        else:
            print(f"No github user for {repo}")


def clone_repos():
    conn = sqlite3.connect(DB)
    query = 'select repo_name from students'
    for row in conn.execute(query):
        repo_name = row[0]
        call_command(
            f'git clone ssh://git@github.com/pyneng/{repo_name}.git'
        )
        print(repo_name)


def create_email_repo_map():
    repos = {}
    conn = sqlite3.connect("students_db.db")
    all_students = "select email, student from students order by student"

    for st_email, st_name in conn.execute(all_students):
        st_name = st_name.lower()
        repo_name = f"online-11-{st_name.replace(' ', '-')}"
        repos[st_email] = repo_name
    return repos


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

    token = os.environ.get("GITHUB_TOKEN")
    g = github.Github(token)
    pyneng_user = g.get_user()

    conn = sqlite3.connect("students_db.db")
    get_st_by_email = "select * from students where email = ?"
    for email, repo_name in repos.items():
        create_template["name"] = repo_name
        try:
            repo = pyneng_user.create_repo(**create_template)
        except github.GithubException:
            failed_to_create[email] = repo_name
        else:
            print("################ OK", repo_name)
        time.sleep(3)

    conn.close()

    if failed_to_create:
        print("### не получилось создать репозиторий")
        pprint(failed_to_create)


if __name__ == "__main__":
    repos_done = {}

    repos_all = create_email_repo_map()
    # for email, repo in repos_all.items():
    #    print(f"{email:35} {repo}")
    create_repos(repos_all)
    add_repo_to_db(repos_all)
    #invite_collaborators()
