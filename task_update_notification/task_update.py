import sys
import subprocess
import re
import os
from pprint import pprint
from collections import defaultdict
import tempfile
import json
import pathlib
from getpass import getpass
import stat
import shutil
from datetime import datetime, timedelta
from glob import glob

import click
import yaml
import pytest
from pytest_jsonreport.plugin import JSONReport
import github



def red(msg):
    return click.style(msg, fg="red")


def green(msg):
    return click.style(msg, fg="green")


def exception_handler(exception_type, exception, traceback):
    """
    sys.excepthook для отключения traceback по умолчанию
    """
    print(f"\n{exception_type.__name__}: {exception}\n")


def call_command(command, verbose=True, return_stdout=False, return_stderr=False):
    """
    Функция вызывает указанную command через subprocess
    и выводит stdout и stderr, если флаг verbose=True.
    """
    result = subprocess.run(
        command,
        shell=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    std = result.stdout
    stderr = result.stderr
    if return_stdout:
        return std
    if return_stderr:
        return result.returncode, stderr
    if verbose:
        print("#" * 20, command)
        if std:
            print(std)
        if stderr:
            print(stderr)
    return result.returncode


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
    repo_name = f"pyneng/{repo}"

    try:
        g = github.Github(token)
        repo_obj = g.get_repo(repo_name)
    except github.GithubException:
        raise AdvPynengError(
            red("Аутентификация по токену не прошла. Задание не сдано на проверку")
        )
    else:
        commits = repo_obj.get_commits(since=since)

        try:
            last = commits[0]
        except IndexError:
            print("За указанный период времени не найдено коммитов")
        else:
            last.create_comment(msg)
            return last


def get_repo(search_pattern=r"advpyneng-\d+-\w+-\w+"):
    git_remote = call_command("git remote -v", return_stdout=True)
    repo_match = re.search(search_pattern, git_remote)
    if repo_match:
        repo = repo_match.group()
        return repo
    else:
        raise AdvPynengError(
            red(
                "Не найден репозиторий advpyneng-3-имя-фамилия. "
                "apyneng надо вызывать в репозитории подготовленном для курса."
            )
        )


def send_tasks_to_check(passed_tasks):
    """
    Функция отбирает все задания, которые прошли
    тесты при вызове apyneng, делает git add для файлов заданий,
    git commit с сообщением какие задания сделаны
    и git push для добавления изменений на Github.
    После этого к этому коммиту добавляется сообщение о том,
    что задания сдаются на проверку с помощью функции post_comment_to_last_commit.
    """
    ok_tasks = [test.replace("test_", "") for test in passed_tasks]
    tasks_num_only = sorted(
        [task.replace("task_", "").replace(".py", "") for task in ok_tasks]
    )
    message = f"Сделаны задания {' '.join(tasks_num_only)}"

    for task in ok_tasks:
        call_command(f"git add {task}")
    call_command(f'git commit -m "{message}"')
    call_command("git push origin main")

    repo = get_repo()
    last = post_comment_to_last_commit(message, repo)
    commit_number = re.search(r'"(\w+)"', str(last)).group(1)
    print(
        green(
            f"Задание успешно сдано на проверку. Комментарий о сдаче задания "
            f"можно посмотреть по ссылке https://github.com/pyneng/{repo}/commit/{commit_number}"
        )
    )


def current_chapter_id():
    """
    Функция возвращает номер текущего раздела, где вызывается apyneng.
    """
    pth = str(pathlib.Path().absolute())
    last_dir = os.path.split(pth)[-1]
    current_chapter = int(last_dir.split("_")[0])
    return current_chapter


def current_dir_name():
    pth = str(pathlib.Path().absolute())
    current_chapter_name = os.path.split(pth)[-1]
    return current_chapter_name


@click.command()
@click.argument("task")
def cli(task):
    token = 0

if __name__ == "__main__":
    cli()
