
import os

from db2docker import container
from db2docker.backends import base


class MariaDBContainer(container.DBContainer):

    @property
    def docker_image(self):
        return "mariadb"

    def get_environment(self):
        return dict(MYSQL_ALLOW_EMPTY_PASSWORD="yes")

    def sql(self, sql):
        return self.run("mysql -e \"%s\"" % sql)

    def sqlfile(self, db_name, sqlfile):
        return self.sql(
            "use %s; SET autocommit=0; source %s; COMMIT;"
            % (db_name, sqlfile))


class MariaDBDockerBackend(base.DBDockerBackend):

    @property
    def container_class(self):
        return MariaDBContainer

    @property
    def volumes(self):
        volumes = super(MariaDBDockerBackend, self).volumes
        if self.args.data is not None:
            volumes[os.path.abspath(self.args.data)] = "/var/lib/mysql"
        return volumes

    def create_db(self):
        cs = "utf8"
        collation = "utf8_general_ci"
        self.response.out(
            "> Creating database (%s)..."
            % self.args.db_name)
        self.response.out(
            self.container.sql(
                "CREATE DATABASE %s CHARACTER SET %s DEFAULT COLLATE %s;"
                % (self.args.db_name, cs, collation)))

    def dump_sql(self):
        if not self.args.outfile:
            return
        outfile = os.path.join(
            os.path.sep, "tmp", "out",
            os.path.basename(self.args.outfile))
        self.response.out(
            self.container.run(
                "sh -c 'mysqldump %s > %s'"
                % (self.args.db_name, outfile)))
