from setuptools import setup

setup(
    name="tsplit",
    version="0.5",
    py_modules=["tsplit"],
    install_requires=[
        "Click",
    ],
    entry_points="""
        [console_scripts]
        tsplit=tsplit:cli
    """,
)

