from setuptools import setup

setup(
    name="update_task_desc",
    version="1.0",
    py_modules=["update_task_desc"],
    install_requires=[
        "Click",
    ],
    entry_points="""
        [console_scripts]
        update_task_desc=update_task_desc:cli
    """,
)

