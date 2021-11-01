from setuptools import setup

setup(
    name="task",
    version="0.1",
    py_modules=["task"],
    install_requires=[
        "Click",
    ],
    entry_points="""
        [console_scripts]
        task=task:cli
    """,
)
