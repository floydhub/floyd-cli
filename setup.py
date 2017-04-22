#!/usr/bin/env python
from setuptools import find_packages, setup

project = "floyd-cli"
version = "0.9.0"

setup(
    name=project,
    version=version,
    description="Command line tool for Floyd",
    author="Floyd",
    author_email="support@floydhub.com",
    url="https://github.com/floydhub/floyd-cli",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    keywords="floyd",
    install_requires=[
        "click>=6.7",
        "clint>=0.5.1",
        "requests>=2.12.4",
        "requests-toolbelt>=0.7.1",
        "marshmallow>=2.11.1",
        "pytz>=2016.10",
        "shortuuid>=0.4.3",
        "tabulate>=0.7.7",
        "pathlib2>=2.2.1",
        "backports.tempfile"
    ],
    setup_requires=[
        "nose>=1.0",
    ],
    dependency_links=[
    ],
    entry_points={
        "console_scripts": [
            "floyd = floyd.main:cli",
            "floyd-dev = floyd.development.dev:cli",
            "floyd-local = floyd.development.local:cli",
        ],
    },
    tests_require=[
        "mock>=1.0.1",
    ],
)
