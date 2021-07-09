import subprocess
from pprint import pprint
import os
import time

import click


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


def run(line):
    subprocess.run(line, shell=True)


def get_active_window_number():
    window_id = call_command(
        "tmux display-message -p '#I'", verbose=True, return_stdout=True
    )
    return window_id.strip()


@click.command()
@click.argument("script_1")
@click.argument("script_2")
def cli(script_1, script_2):
    """
    Микроскрипт для лекции по Rich.
    Запускает два скрипта в панелях tmux. Смысл показать как тот же самый код выглядит
    с использованием Rich и без.
    """

    if not os.environ.get("TMUX"):
        raise SystemExit(click.style("Скрипт надо запускать в tmux", fg="red"))

    window = get_active_window_number()
    run(f'tmux send-keys -t {window}.0 "clear" Enter')
    run(f'tmux send-keys -t {window}.0 "python {script_1}" Enter')
    run(f"tmux split-window -h")
    run("tmux select-pane -t 1")
    run(f'tmux send-keys -t {window}.1 "clear" Enter')
    run(f'tmux send-keys -t {window}.1 "python {script_2}" Enter')



if __name__ == "__main__":
    cli()
