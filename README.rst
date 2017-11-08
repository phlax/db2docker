DB2Docker
=========

Pipe an sql file into docker, optionally transform the data and pipe it back out


|build| |coverage|


Installation
------------

For installation into any python environment

::

  pip install db2docker


For development install

::

  pip install -e git+https://github.com/phlax/db2docker#egg=db2docker


Requirements
------------

You must have docker running on your system, and the user running db2docker must have
the necessary privileges to use it.


Usage - load sql to docker data
-------------------------------

Load sql file into db, and create data volume

::

   db2docker /path/to/input.sql --data=/path/to/data


You can then use the data path to start a database container, for example using mariadb

::

   docker run --name some-mariadb -v /path/to/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mariadb


Usage - Scrub passwords from an sql file
----------------------------------------

Load sql file into db, blank passwords from ``accounts_user`` table, and dump back to sql

First, create an sql "pipe" file at path ``/path/to/pipe.sql``, containing

::

   update `accounts_user` set `password`="";


Then you can use db2docker to apply the sql to the data

::

   db2docker /path/to/input.sql --pipe=/path/to/pipe.sql --data=/path/to/data


If you only want an sql file containing the changes you can:

::

   db2docker /path/to/input.sql --pipe=/path/to/pipe.sql --out=/path/to/output.sql


You can specify multiple sql files in the pipeline

::

   db2docker /path/to/input.sql --pipe=/path/to/pipe1.sql --pipe=/path/to/pipe2.sql --out=/path/to/output.sql



.. |build| image:: https://img.shields.io/travis/phlax/db2docker/master.svg?style=flat-square
        :alt: Build Status
        :target: https://travis-ci.org/phlax/db2docker/branches


.. |coverage| image:: https://img.shields.io/codecov/c/github/phlax/db2docker/master.svg?style=flat-square
        :target: https://codecov.io/gh/phlax/db2docker/branch/master
        :alt: Test Coverage
