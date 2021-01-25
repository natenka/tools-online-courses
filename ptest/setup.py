from setuptools import setup

setup(
    name="ptest",
    version="1.0",
    py_modules=["ptest"],
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
        ptest=ptest:cli
    """,
)
