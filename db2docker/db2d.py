
from db2docker import cli
from db2docker.backends.mariadb import MariaDBDockerBackend


class DB2Docker(object):

    def __init__(self):
        self._db_types = {}

    @property
    def types(self):
        return self._db_types

    def register(self, name, klass):
        self._db_types[name] = klass

    def run(self, *args):
        parsed_args = cli.Args().parse(*args)
        response = cli.Response()
        self.types[parsed_args.container_type](
            parsed_args, response).run()


db2d = DB2Docker()
db2d.register("mariadb", MariaDBDockerBackend)
