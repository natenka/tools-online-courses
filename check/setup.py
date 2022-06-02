from setuptools import setup

setup(
    name="check",
    version="1.3",
    py_modules=["check"],
    install_requires=[
        "Click",
        "pyyaml",
        "pytest",
        "pytest-clarity",
        "pytest-json-report",
        "requests",
        "PyGithub",
        "six",
    ],
    entry_points="""
        [console_scripts]
        check=check:cli
    """,
)
