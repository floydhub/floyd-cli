#!/usr/bin/env python
from setuptools import find_packages, setup

project = "floyd-cli"
version = "0.1.0"

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
        "requests>=2.12.4",
        "marshmallow>=2.11.1",
        "PyYAML>=3.12",
    ],
    setup_requires=[
    ],
    dependency_links=[
    ],
    entry_points={
        "console_scripts": [
            "floyd = floyd.main:cli",
        ],
    },
    tests_require=[
        "mock>=1.0.1",
    ],
)
