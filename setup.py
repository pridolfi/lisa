# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='lisa',
    version='0.1.0',
    description='Light Implementation of Secure Automation',
    long_description=readme,
    author='Pablo Ridolfi',
    author_email='pabloridolfi@gmail.com',
    url='https://github.com/pridolfi/lisa',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    scripts=['nodes/linux/lisa_run.py', 'nodes/esp32/lisa_esp32_generator.py']
)
