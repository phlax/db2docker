# -*- coding: utf-8 -*-

"""DB2Docker
"""

from setuptools import setup, find_packages


setup(
    name='db2docker',
    version='0.0.1',
    description="Database to docker container",
    long_description=(
        'Convert an sql file to docker volume, '
        'with optional transforms and/or dumping'),
    url='https://github.com/phlax/docker2db',
    author='Ryan Northey',
    author_email='rnorthey@mozilla.com',
    license='GPL3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GPL3',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='docker mariadb convert',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        "docker==2.5.1",
        "pytest",
        "pytest-mock",
        "coverage",
        "pytest-coverage",
        "codecov",
        "flake8"],
    entry_points={
        'console_scripts': [
            'db2docker = db2docker.runner:main',
        ]})
