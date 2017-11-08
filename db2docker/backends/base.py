
import os

from contextlib import contextmanager

from db2docker import container


class DBDockerBackend(object):

    def __init__(self, parsed_args, response):
        self.args = parsed_args
        self.response = response
        self.container = self.container_class(
            container_name=self.args.container_name,
            volumes=self.volumes,
            db_name=self.args.db_name,
            response=self.response)

    @property
    def container_class(self):
        return container.DBContainer

    @contextmanager
    def db(self):
        self.container.start()
        try:
            yield self
        finally:
            self.container.stop()
            self.container.rm()

    @property
    def volumes(self):
        volumes = {
            os.path.dirname(
                os.path.abspath(
                    self.args.sql_file)): "/tmp/sql"}
        if self.args.outfile is not None:
            volumes[
                os.path.dirname(
                    os.path.abspath(
                        self.args.outfile))] = "/tmp/out"
        if self.args.pipeline:
            for i, pipeline in enumerate(self.args.pipeline):
                volumes[
                    os.path.dirname(
                        os.path.abspath(
                            pipeline))] = "/tmp/pipeline%s" % i
        return volumes

    def load_sql(self, sql_file):
        self.create_db()
        self.response.out(
            "> Loading SQL file (%s)..."
            % self.args.sql_file)
        self.response.out(
            self.container.sqlfile(
                self.args.db_name, sql_file))

    def pipeline_sql(self):
        if not self.args.pipeline:
            return
        for i, pipeline in enumerate(self.args.pipeline):
            _pipeline = os.path.join(
                os.path.sep, "tmp", "pipeline%s" % i,
                os.path.basename(pipeline))
            ct = self.container
            self.response.out(
                ct.sqlfile(
                    self.args.db_name, _pipeline))

    def run(self):
        sql_file = os.path.join(
            os.path.sep, "tmp", "sql",
            os.path.basename(self.args.sql_file))
        with self.db():
            self.load_sql(sql_file)
            self.pipeline_sql()
            self.dump_sql()
