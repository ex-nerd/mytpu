from setuptools import setup

import os
import sys
import re

install_requires = []
if sys.version_info < (3, 10):
    raise Exception("mytpu requires Python 3.10 or higher.")

# Might need "hyper" for http/2 but so far getting along without it
install_requires += ["requests", "attrs", "cattrs", "argparse"]

# Load the version by reading prep.py, so we don't run into
# dependency loops by importing it into setup.py
version = None
with open(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "mytpu", "__init__.py")
) as file:
    for line in file:
        m = re.search(r"__version__\s*=\s*(.+?\n)", line)
        if m:
            version = eval(m.group(1))
            break

setup_args = dict(
    name="mytpu",
    version=version,
    author="Chris Petersen",
    author_email="geek@ex-nerd.com",
    url="https://github.com/ex-nerd/mytpu",
    license="MIT",
    description="",
    long_description=open("README.md").read(),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "mytpu = mytpu.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
)

if __name__ == "__main__":
    setup(**setup_args)
