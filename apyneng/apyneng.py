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


TASK_DIRS = [
    "01_pytest_basics",
    "02_type_annotations",
    "04_click",
    "05_logging",
    "07_closure",
    "08_decorators",
    "09_oop_basics",
    "10_oop_special_methods",
    "11_oop_method_decorators",
    "12_oop_inheritance",
    "13_data_classes",
    "14_generators",
    "17_async_libraries",
    "18_using_asyncio",
]
TASK_DIRS_WITHOUT_TESTS = ["01", "05", "17", "18"]


class AdvPynengError(Exception):
    """
    Ошибка в использовании/работе скрипта apyneng
    """


def red(msg):
    return click.style(msg, fg="red")


def green(msg):
    return click.style(msg, fg="green")


def exception_handler(exception_type, exception, traceback):
    """
    sys.excepthook для отключения traceback по умолчанию
    """
    print(f"\n{exception_type.__name__}: {exception}\n")


class CustomTasksType(click.ParamType):
    """
    Класс создает новый тип для click и преобразует
    допустимые варианты строк заданий в отдельные файлы тестов.

    Кроме того проверяет есть ли такой файл в текущем каталоге
    и оставляет только те, что есть.
    """

    name = "CustomTasksType"

    def convert(self, value, param, ctx):
        # for some reason click can call this method with parsed args
        # this allowes to return parsed value as is
        if isinstance(value, tuple):
            return value

        regex = (
            r"(?P<all>all)|"
            r"(?P<number_star>\d\*)|"
            r"(?P<letters_range>\d[a-i]-[a-i])|"
            r"(?P<numbers_range>\d-\d)|"
            r"(?P<single_task>\d[a-i]?)"
        )
        current_chapter = current_dir_name()
        if current_chapter not in TASK_DIRS:
            task_dirs_line = "\n    ".join(
                [d for d in TASK_DIRS if not d.startswith("task")]
            )
            self.fail(
                red(
                    f"\nСкрипт нужно вызывать из каталогов с заданиями:"
                    f"\n    {task_dirs_line}"
                )
            )

        tasks_list = re.split(r"[ ,]+", value)
        current_chapter = current_chapter_id()
        test_files = []
        task_files = []
        for task in tasks_list:
            match = re.fullmatch(regex, task)
            if match:
                if task == "all":
                    test_files = sorted(glob(f"test_task_{current_chapter}_*.py"))
                    task_files = glob(f"task_{current_chapter}_*.py")
                    break
                else:
                    if match.group("letters_range"):
                        task = f"{task[0]}[{task[1:]}]"  # convert 1a-c to 1[a-c]
                    elif match.group("numbers_range"):
                        task = f"[{task}]"  # convert 1-3 to [1-3]

                    test_files += glob(f"test_task_{current_chapter}_{task}.py")
                    task_files += glob(f"task_{current_chapter}_{task}.py")
            else:
                self.fail(
                    red(
                        f"Данный формат не поддерживается {task}. "
                        "Допустимые форматы: 1, 1a, 1b-d, 1*, 1-3"
                    )
                )
        tasks_with_tests = set([test.replace("test_", "") for test in test_files])
        tasks_without_tests = set(task_files) - tasks_with_tests
        return sorted(test_files), sorted(tasks_without_tests)


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
    ok_tasks = [
        re.sub(r".*(task_\d+_\d+.py)", r"\1", filename)
        for filename in passed_tasks
    ]
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


def test_run_for_github_token():
    """
    Функция добавляет тестовое сообщение к последнем коммиту на 2 недели
    """
    message = "Проверка работы токена прошла успешно"
    repo = get_repo()
    last = post_comment_to_last_commit(message, repo)
    commit_number = re.search(r'"(\w+)"', str(last)).group(1)
    print(
        green(
            f"Комментарий можно посмотреть по ссылке "
            f"https://github.com/pyneng/{repo}/commit/{commit_number}"
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


def parse_json_report(report):
    """
    Отбирает нужные части из отчета запуска pytest в формате JSON.
    Возвращает список тестов, которые прошли.
    """
    if report and report["summary"]["total"] != 0:
        all_tests = defaultdict(list)
        summary = report["summary"]

        test_names = [test["nodeid"] for test in report["collectors"][0]["result"]]
        for test in report["tests"]:
            name = test["nodeid"].split("::")[0]
            all_tests[name].append(test["outcome"] == "passed")
        all_passed_tasks = [name for name, outcome in all_tests.items() if all(outcome)]
        return all_passed_tasks
    else:
        return []


@click.command(
    context_settings=dict(
        ignore_unknown_options=True, help_option_names=["-h", "--help"]
    )
)
@click.argument("tasks", default="all", type=CustomTasksType())
@click.option(
    "--disable-verbose", "-d", is_flag=True, help="Отключить подробный вывод pytest"
)
@click.option(
    "--check",
    "-c",
    is_flag=True,
    help=(
        "Сдать задания на проверку. "
        "При добавлении этого флага, "
        "не выводится traceback для тестов."
    ),
)
@click.option("--debug", is_flag=True, help="Показывать traceback исключений")
@click.option("--test-token", is_flag=True, help="Проверить работу токена")
def cli(tasks, disable_verbose, check, debug, test_token):
    """
    Запустить тесты для заданий TASKS. По умолчанию запустятся все тесты.

    Примеры запуска:

    \b
        apyneng --test-token проверить работу токена
        apyneng              запустить все тесты для текущего раздела
        apyneng 1,2a,5       запустить тесты для заданий 1, 2a и 5
        apyneng 1,2a-c,5     запустить тесты для заданий 1, 2a, 2b, 2c и 5
        apyneng 1,2*         запустить тесты для заданий 1, все задания 2 с буквами и без
        apyneng 1,3-5        запустить тесты для заданий 1, 3, 4, 5
        apyneng 1-5 -c       запустить тесты и сдать на проверку задания,
                             которые прошли тесты.

    Флаг -d отключает подробный вывод pytest, который включен по умолчанию.
    Флаг -c сдает на проверку задания (пишет комментарий на github)
    для которых прошли тесты.
    Для сдачи заданий на проверку надо сгенерировать токен github.
    Подробнее в инструкции: https://advpyneng.github.io/docs/apyneng-prepare/
    """
    token_error = red(
        "Для сдачи заданий на проверку надо сгенерировать токен github. "
        "Подробнее в инструкции: https://advpyneng.github.io/docs/apyneng-prepare/"
    )
    if test_token:
        test_run_for_github_token()
        print(green("Проверка токена прошла успешно"))
        raise click.Abort()

    if not debug:
        sys.excepthook = exception_handler

    json_plugin = JSONReport()
    pytest_args_common = ["--json-report-file=none", "--disable-warnings"]

    if disable_verbose:
        pytest_args = [*pytest_args_common, "--tb=short"]
    else:
        pytest_args = [*pytest_args_common, "-vv"]

    # если добавлен флаг -c нет смысла выводить traceback,
    # так как скорее всего задания уже проверены предыдущими запусками.
    if check:
        pytest_args = [*pytest_args_common, "--tb=no"]

    # после обработки CustomTasksType, получаем два списка файлов
    test_files, tasks_without_tests = tasks

    # запуск pytest
    pytest.main(test_files + pytest_args, plugins=[json_plugin])

    # получить результаты pytest в формате JSON
    # passed_tasks это задания у которых есть тесты и тесты прошли
    passed_tasks = parse_json_report(json_plugin.report)

    if passed_tasks or tasks_without_tests:
        # сдать задания на проверку через github API
        if check:
            token = os.environ.get("GITHUB_TOKEN")
            if not token:
                raise AdvPynengError(token_error)
            send_tasks_to_check(passed_tasks + tasks_without_tests)


if __name__ == "__main__":
    cli()
