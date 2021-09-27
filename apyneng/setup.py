from setuptools import setup

setup(
    name="apyneng",
    version="0.7",
    py_modules=["apyneng"],
    install_requires=[
        "Click",
        "pyyaml",
        "pytest",
        "pytest-clarity",
        "pytest-json-report",
        "PyGithub",
        "six",
    ],
    entry_points="""
        [console_scripts]
        apyneng=apyneng:cli
    """,
)
