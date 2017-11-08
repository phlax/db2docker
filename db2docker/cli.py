
import argparse
import os
import sys


class ValidatingArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        self.validators = {}
        super(ValidatingArgumentParser, self).__init__(*args, **kwargs)

    def validate(self, results, *args, **kwargs):
        for k, validators in self.validators.items():
            for validator in validators:
                try:
                    validator(k, getattr(results, k), results)
                except Exception as e:
                    self.error(str(e))

    def add_argument(self, *args, **kwargs):
        validators = kwargs.pop("validators", [])
        argument = super(
            ValidatingArgumentParser,
            self).add_argument(*args, **kwargs)
        if validators:
            self.validators[argument.dest] = validators
        return argument

    def parse_known_args(self, *args, **kwargs):
        result = super(
            ValidatingArgumentParser,
            self).parse_known_args(*args, **kwargs)
        self.validate(result[0], *args, **kwargs)
        return result


def file_exists(k, filepath, results):
    if not os.path.exists(filepath):
        raise ValueError("Missing SQL file: %s" % filepath)


def save_to_something(k, data, results):
    if not data and not results.outfile:
        raise ValueError(
            "You must specify either an out sql file or a data mount")


def all_files_exist(k, filepaths, results):
    if filepaths:
        all(file_exists(k, f, results) for f in filepaths)


class Args(object):

    def __init__(self):
        self.parser = ValidatingArgumentParser()
        self.add_args()

    def add_args(self):
        from db2docker.db2d import db2d

        self.parser.add_argument(
            "sql_file",
            validators=[file_exists])
        self.parser.add_argument(
            "--pipe",
            action="append",
            dest="pipeline",
            validators=[all_files_exist])
        self.parser.add_argument(
            "--out", dest="outfile")
        self.parser.add_argument(
            "--data", dest="data",
            validators=[save_to_something])
        self.parser.add_argument(
            "--container-type",
            dest="container_type",
            default="mariadb",
            choices=db2d.types.keys())
        self.parser.add_argument(
            "--container-name",
            dest="container_name",
            default="dockerdb-container")
        self.parser.add_argument(
            "--db-name",
            dest="db_name",
            default="dockerdb")

    def parse(self, *args):
        return self.parser.parse_args(args)


class Response(object):

    def out(self, msg, ending="\n", flush=True):
        sys.stdout.write("%s%s" % (msg, ending))
        if flush:
            sys.stdout.flush()
