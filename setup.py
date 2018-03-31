#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['ont_fast5_api', 'numpy']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Michael Hall",
    author_email='mbhall88@gmail.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Simulate repeating a nanopore experiment.",
    entry_points={
        'console_scripts': [
            'taeper=taeper.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='taeper',
    name='taeper',
    packages=find_packages(include=['taeper']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/mbhall88/taeper',
    version='0.1.0',
    zip_safe=False,
)
