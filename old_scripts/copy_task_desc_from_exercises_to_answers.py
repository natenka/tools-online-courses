import time
import re
import subprocess
import os
from glob import glob

spath = "/home/vagrant/repos/pyneng-tasks/pyneng-examples-exercises-en/exercises/"
dpath = "/home/vagrant/repos/pyneng-tasks/pyneng-answers-en/answers/"


def copy_tests():
    """Start from dpath"""
    dirs = sorted(glob("[0-2]*"))
    for d in dirs:
        os.chdir(d)
        tests = sorted(glob("test_*.py"))
        for test in tests:
            subprocess.run(f"cp {spath}{d}/{test} {dpath}{d}/{test}", shell=True)
        os.chdir("..")


# copy task desc
dirs = sorted(glob("[0-2]*"))
for d in dirs:
    os.chdir(d)
    tasks = sorted(glob("task_*.py"))
    for task in tasks:
        try:
            with open(f"{spath}{d}/{task}") as source, open(f"{dpath}{d}/{task}") as dst:
                src_desc = source.read()
                m = re.search(r'""".+?"""', src_desc, re.DOTALL)
                task_description = m.group()
                dest_read = dst.read()
                replaced_text = re.sub(r'""".+?"""', task_description, dest_read, flags=re.DOTALL)
            with open(f"{dpath}{d}/{task}", "w") as dst_wr:
                dst_wr.write(replaced_text)
            print(f"Task {task} DONE")
            time.sleep(0.5)
        except FileNotFoundError:
            print(f"FileNotFoundError {task}")
    os.chdir("..")
