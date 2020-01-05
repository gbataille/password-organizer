from setuptools import setup, find_packages
import os

import password_organizer

_version = os.environ.get("VERSION_OVERRIDE", password_organizer.__version__)

with open('requirements.txt') as fp:
    install_requires = fp.read().strip().split('\n')

with open('requirements_test.txt') as fp:
    tests_require = fp.read().strip().split('\n')

setup(
    name='password_organizer',
    version=_version,
    author='Gregory Bataille',
    author_email='gregory.bataille@gmail.com',
    packages=find_packages(),
    scripts=[
        'bin/passsword-organizer',
    ],
    license='MIT License',
    url='',
    description='Password organizer CLI for a number of password vault technology',
    long_description='',
    install_requires=install_requires,
    tests_require=tests_require,
)
