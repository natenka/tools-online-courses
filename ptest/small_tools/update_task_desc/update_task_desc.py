from glob import glob
import re
import pathlib
import os

import click


@click.command()
@click.option("--debug", "-d")
def cli(debug):
    pth = str(pathlib.Path().absolute())
    current_chapter = os.path.split(pth)[-1]

    tasks_path = (
        f"/home/vagrant/repos/pyneng-tasks/pyneng-examples-exercises/"
        f"exercises/{current_chapter}/"
    )

    answers = sorted(glob("task_*.py"))
    new_answers = {}

    for t in answers:
        with open(t) as ans, open(f"{tasks_path}{t}") as task:
            content_ans = ans.read()
            content_task = task.read()

            docstring = re.search(r'""".+?"""', content_task, re.DOTALL).group()
            s = re.compile(r'""".+?"""', re.DOTALL)
            new_content_ans = re.sub(s, docstring, content_ans, count=1)
            new_answers[t] = new_content_ans

    for t in answers:
        with open(t, "w") as ans:
            ans.write(new_answers[t])


if __name__ == "__main__":
    cli()

