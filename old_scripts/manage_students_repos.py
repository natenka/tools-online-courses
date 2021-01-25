# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from github import Github


def get_student_folders():
    all_dirs = os.listdir(".")
    all_students_dirs = [d for d in all_dirs if d.startswith("online-10")]
    return sorted(all_students_dirs)


def call_command(list_of_dirs, command):

    for d in list_of_dirs:
        subprocess.call(command, shell=True)


def push_repo_git_master(repo, commit_message=""):

    git_commands = [
        "git add .",
        'git commit -m "{}"'.format(commit_message),
        "git push origin master",
    ]

    os.chdir(repo)
    for command in git_commands:
        subprocess.call(command, shell=True)
    os.chdir("..")
    print("\n" + "#" * 60)


def push_git_master(list_of_dirs, commit_message=""):

    git_commands = [
        "git add .",
        'git commit -m "{}"'.format(commit_message),
        "git push origin master",
    ]

    for d in list_of_dirs:
        os.chdir(d)
        for command in git_commands:
            subprocess.call(command, shell=True)
        os.chdir("..")
        print("\n" + "#" * 60)


def git_pull(list_of_dirs):

    for d in list_of_dirs:
        os.chdir(d)
        print("=" * 40)
        print(d)
        subprocess.call("git pull", shell=True)
        os.chdir("..")


def git_checkout(list_of_dirs, branch="master"):

    for d in list_of_dirs:
        os.chdir(d)
        print(d)
        subprocess.call("git checkout {}".format(branch), shell=True)
        os.chdir("..")


def show_task(list_of_dirs, task):

    for d in list_of_dirs:
        command = "cat {}/exercises/{}".format(d, task)
        subprocess.call(command, shell=True)


def git_status(list_of_dirs):
    for d in list_of_dirs:
        os.chdir(d)
        print(d)
        subprocess.call("git status", shell=True)
        os.chdir("..")


def git_log(list_of_dirs):
    for d in list_of_dirs:
        os.chdir(d)
        print("#" * 60)
        print(d)
        subprocess.call("git log -1", shell=True)
        os.chdir("..")


def post_comment_to_last_commit(msg, repo, delta_days=14):
    """
    Написать комментарий о сдаче заданий в последнем коммите.
    Комментарий пишется через Github API.

    Для работы функции должен быть настроен git.
    Функция пытается определить имя пользователя git из вывода git config --list,
    Если это не получается, запрашивает имя пользователя.

    Пароль берется из переменной окружения GITHUB_PASS или запрашивается.
    """
    token = os.environ.get("GITHUB_TOKEN")
    since = datetime.now() - timedelta(days=delta_days)

    g = Github(token)
    repo_name = f"pyneng/{repo}"
    print(repo_name)
    repo_obj = g.get_repo(repo_name)
    commits = repo_obj.get_commits(since=since)

    try:
        last = commits[0]
    except IndexError:
        print("За указанный период времени не найдено коммитов")
    else:
        last.create_comment(msg)


if __name__ == "__main__":
    # st_dir = sys.argv[1]
    # dirs = get_student_folders()
    # show_task(dirs, task='04_basic_scripts/task_4_3a.py')
    # git_checkout(dirs, 'master')
    # git_pull(dirs)
    # git_log(dirs)
    # push_git_master(dirs, commit_message='Добавила задания в репозиторий')
    # git_status(dirs)
    dirs = [
        "online-9-vitaliy-chistyakov",
        "online-9-vladislav-kiyanovskiy",
        "online-8-sergey-smirnov",
        "online-9-oleg-vorobev",
    ]
    repo = "/home/vagrant/repos/pyneng-10/pyneng-online-10-jan-apr-2021"

    commands = [
        # 'cp -R {}/exercises ./{}',
        # 'cp -R {}/.gitignore ./{}',
        # 'cp -R {}/README.md ./{}',
        "cp -R /home/vagrant/repos/pyneng-10/pyneng-online-10-jan-apr-2021/ptest.py ./{}",
        # 'cp -R {}/setup.py ./{}',
        # 'cp -R {}/github_token_stored.py ./{}',
    ]
    for st_dir in dirs:
        for command in commands:
            subprocess.run(command.format(st_dir), shell=True)

        push_repo_git_master(st_dir, commit_message="Исправлен ptest")
        time.sleep(0.5)
        msg = "Обновлен скрипт ptest.py. Локально надо дать команду git pull"
        post_comment_to_last_commit(msg, st_dir, delta_days=14)
        time.sleep(1)

    # push_git_master(dirs, commit_message='Добавила задания в репозиторий')
