"""
Script to open task answer file
"""
import os
import re
import subprocess
import click


TASK_ANSWERS = "/home/vagrant/repos/general/advpyneng-answers/exercises"
TASK_DIRS = {
    1: "01_pytest_basics",
    2: "02_type_annotations",
    4: "04_click",
    5: "05_logging",
    7: "07_closure",
    8: "08_decorators",
    9: "09_oop_basics",
    10: "10_oop_special_methods",
    11: "11_oop_method_decorators",
    12: "12_oop_inheritance",
    13: "13_data_classes",
    14: "14_generators",
    17: "17_async_libraries",
    18: "18_using_asyncio",
}



class TaskAnswer(click.ParamType):
    """
    По номеру задания возвращает полный путь к файлу задания
    """
    def convert(self, value, param, ctx):
        match_task = re.search(r"(?P<task_dir>\d+)\.(?P<task_number>\d+\w?)", value)
        if match_task:
            task_dir_number = int(match_task.group("task_dir"))
            task_number = match_task.group("task_number")
            if task_dir_number not in TASK_DIRS:
                self.fail(red("Такого каталога нет"))
            task_dir = TASK_DIRS.get(task_dir_number)
            task_filename = f"task_{task_dir_number}_{task_number}.py"
            task_full_path = os.path.join(TASK_ANSWERS, task_dir, task_filename)
            return task_full_path
        elif "/" in value:
            return value
        else:
            self.fail(red("Такого задания нет"))


@click.command()
@click.argument("task", type=TaskAnswer())
def cli(task):
    print(f"{task=}")
    subprocess.run(f"vim -O {task}", shell=True)


if __name__ == "__main__":
    cli()
