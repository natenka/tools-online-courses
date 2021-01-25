# -*- coding: utf-8 -*-

import os
import re
import subprocess
from glob import glob
import pathlib
from datetime import datetime, timedelta

import click
import pytest
import github


chapter_to_folder_map = {
    "4": "04_data_structures",
    "5": "05_basic_scripts",
    "6": "06_control_structures",
    "7": "07_files",
    "9": "09_functions",
    "11": "11_modules",
    "12": "12_useful_modules",
    "15": "15_module_re",
    "17": "17_serialization",
    "18": "18_ssh_telnet",
    "19": "19_concurrent_connections",
    "20": "20_jinja2",
    "21": "21_textfsm",
    "22": "22_oop_basics",
    "23": "23_oop_special_methods",
    "24": "24_oop_inheritance",
}


def SyncError(Exception):
    pass


def convert_task_arg(value, current_chapter):
    if value == "all":
        return value
    regex = (
        r"(?P<all>all)|"
        r"(?P<number_star>\d\*)|"
        r"(?P<letters_range>\d[a-i]-[a-i])|"
        r"(?P<numbers_range>\d-\d)|"
        r"(?P<single_task>\d[a-i]?)"
    )
    tasks_list = re.split(r"[ ,]+", value)
    task_files_glob = []
    for task in tasks_list:
        match = re.fullmatch(regex, task)
        if match:
            if match.group("letters_range"):
                task = f"{task[0]}[{task[1:]}]"  # convert 1a-c to 1[a-c]
            elif match.group("numbers_range"):
                task = f"[{task}]"  # convert 1-3 to [1-3]

            task_files_glob.append(f"task_{current_chapter}_{task}.py")
        else:
            print(
                f"Данный формат не поддерживается {task}. "
                "Допустимые форматы: 1, 1a, 1b-d, 1*, 1-3"
            )
    return task_files_glob


def call_command(command, verbose=True):
    result = subprocess.run(
        command,
        shell=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    std = result.stdout + result.stderr
    if verbose:
        print("#" * 20, command)
        if std:
            print(std)
    return std


def get_chapter_to_folder_map(path):
    all_dirs = os.listdir(path)
    return {int(d.split("_")[0]): d for d in all_dirs if d[0].isdigit()}


def git_checkout(branch="master"):
    call_command("git checkout {}".format(branch))


def git_pull():
    for i in range(2):
        result = call_command("git pull")
        if i == 0:
            if "Already up-to-date." in result:
                return True
        else:
            if "Already up-to-date." not in result:
                raise SyncError
    return True


def copy_tasks_to_task_check(folder_id, task_list):
    folder_name = chapter_to_folder_map[folder_id]
    path = f"exercises/{folder_name}/"
    if task_list == "all":
        # checkout folder
        call_command(f"git checkout master {path}")
    else:
        tasks = []
        for t_glob in task_list:
            tasks.extend(glob(f"exercises/{folder_name}/{t_glob}"))

        for task in tasks:
            call_command(f"git checkout master {task}")

    call_command("git status")
    try:
        click.secho("Please check git status", fg="red", bold=True)
        # input("Нажмите Enter для продолжения/Ctrl-C для остановки")
    except KeyboardInterrupt:
        print("Files copied, but not commited")
        return
    git_commands = [
        "git add .",
        'git commit -m "Загрузила решения в ветку task_check"',
        "git push origin task_check",
    ]

    for command in git_commands:
        result = call_command(command)


def git_create_task_check():
    output = call_command("git branch -a")
    if "task_check" in output:
        return
    else:
        call_command("git checkout -b task_check")
        call_command("git push -u origin HEAD")


def run_tests(folder_number, task_list):
    pth = str(pathlib.Path().absolute())
    for folder in folder_number:
        folder_name = chapter_to_folder_map[folder]
        task_path = f"exercises/{folder_name}/"
        os.chdir(task_path)

        pytest_args = ["--disable-warnings", "--no-hints", "--tb=no"]
        if task_list == "all":
            pytest.main(pytest_args)
        else:
            tests = []
            for t_glob in task_list:
                tests.extend(glob(f"test_{t_glob}"))
            pytest.main(tests + pytest_args)

        os.chdir(pth)

        input("Нажмите Enter для открытия заданий в vim/Ctrl-C для остановки")
        # open tasks in vim
        if task_list == "all":
            subprocess.run(f"vim -p exercises/{folder_name}/task_*.py", shell=True)
        else:
            tasks_str = " ".join(
                [f"exercises/{folder_name}/{task}" for task in task_list]
            )
            subprocess.run(f"vim -p {tasks_str}", shell=True)


def post_comment_to_last_commit(msg, delta_days=14):
    git_remote = call_command("git remote -v")
    repo_match = re.search(r"online-\d+-\w+-\w+", git_remote)
    if repo_match:
        repo = repo_match.group()
    else:
        raise ValueError("Не найден репозиторий online-10-имя-фамилия. ")

    token = os.environ.get("GITHUB_TOKEN")
    since = datetime.now() - timedelta(days=delta_days)
    repo_name = f"pyneng/{repo}"

    try:
        g = github.Github(token)
        repo_obj = g.get_repo(repo_name)
    except github.GithubException:
        raise ValueError(
            "Аутентификация по токену не прошла. Задание не сдано на проверку"
        )
    else:
        branch_task_check = repo_obj.get_branch("task_check")
        last = branch_task_check.commit
        last.create_comment(msg)


def upload_checked_tasks(tasks):
    message = (
        f"Проверены задания {tasks}. Всё отлично!\n"
        "Не забудьте посмотреть варианты решения\n"
        "```\n"
        "ptest -a\n"
        "```\n\n"
        "Как посмотреть проверенные задания на github: https://pyneng.github.io/docs/task-check-github/\n"
        "в командной строке: https://pyneng.github.io/docs/checked-tasks-git/\n"
    )
    c_message = f"Проверены задания {tasks}"
    call_command("git add .")
    call_command(f'git commit -m "{c_message}"')
    call_command("git push origin task_check")
    post_comment_to_last_commit(message)


@click.command()
@click.argument("folder_number", nargs=-1)
@click.option("--tasks", "-t", default="all")
@click.option("--check-done", "-c", help="Все проверено, запушить на github")
def cli(folder_number, tasks, check_done):
    """
    Примеры запуска:

    \b
    check 7 -t 1,2a,5   запустить проверку для заданий 7.1, 7.2a и 7.5
    check 5             запустить проверку для заданий 5 раздела
    check 5 -t 1,2*     запустить проверку для заданий 5.1, все задания 5.2 с буквами и без
    check 3 4 5         запустить проверки для всех заданий 3, 4, 5 разделов
    """
    if check_done:
        upload_checked_tasks(check_done)

    else:
        git_checkout("master")
        git_pull()
        git_create_task_check()
        git_checkout("task_check")

        if tasks != "all":
            tasks = convert_task_arg(tasks, folder_number[0])
        for folder in folder_number:
            if folder in chapter_to_folder_map:
                copy_tasks_to_task_check(folder, tasks)
            else:
                print("Такого раздела нет", folder)

        run_tests(folder_number, tasks)


if __name__ == "__main__":
    cli()
