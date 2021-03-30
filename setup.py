import os
import pathlib

import pkg_resources
from setuptools import find_packages, setup

BASEDIR = os.path.dirname(os.path.abspath(__file__))


def parse_reqs(reqs_file):
    install_reqs = list()
    with pathlib.Path(reqs_file).open() as requirements_txt:
        install_reqs = [
            str(requirement)
            for requirement in pkg_resources.parse_requirements(requirements_txt)
        ]
    return install_reqs


requirements = parse_reqs(os.path.join(BASEDIR, "requirements.txt"))

setup(
    name="veedrive",
    version="0.1",
    description="Media serving and presentation persistence service for VeeOne",
    author="Pawel Podhajski",
    author_email="pawel.podhajski@epfl.ch",
    license="LGPL",
    packages=find_packages(),
    zip_safe=False,
    install_requires=requirements,
)
