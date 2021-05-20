from setuptools import setup

setup(
    name="acheck",
    version="1.0",
    py_modules=["acheck"],
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
        acheck=acheck:cli
    """,
)
