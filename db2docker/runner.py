#!/home/phlax/.virtualenvs/dbdock/bin/python3

# -*- coding: utf-8 -*-

import sys

from db2docker.db2d import db2d


def main():
    db2d.run(*sys.argv[1:])
