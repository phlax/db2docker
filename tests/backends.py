import os
from contextlib import contextmanager

from db2docker.backends.base import DBDockerBackend
from db2docker.container import DBContainer
from db2docker import cli


class DummyDBContainer(DBContainer):
    docker_image = "dummy"
    sqlfile_called = None

    def sqlfile(self, db_name, sqlfile):
        DummyDBContainer.sqlfile_called = (
            (DummyDBContainer.sqlfile_called or ())
            + ((db_name, sqlfile), ))


class DummyDBDockerBackend(DBDockerBackend):
    container_class = DummyDBContainer
    create_db_called = False

    def create_db(self, *args, **kwargs):
        DummyDBDockerBackend.create_db_called = True


def test_backend_base_defaults(tmpdir):
    foodir = tmpdir.mkdir("foo")
    sqlfile = os.path.join(str(foodir), "bar.sql")
    with open(sqlfile, "w") as f:
        f.write("some sql")
    args = (sqlfile, "--data=/some/data")
    parsed_args = cli.Args().parse(*args)

    response = cli.Response()
    backend = DBDockerBackend(parsed_args, response)
    assert backend.args == parsed_args
    assert backend.response == response
    assert backend.container_class == DBContainer
    assert isinstance(
        backend.container,
        backend.container_class)
    assert backend.container.response == response
    assert backend.container.container_name == parsed_args.container_name
    assert backend.container.db_name == parsed_args.db_name
    assert backend.volumes == backend.container.volumes


def test_backend_base_db(mocker, tmpdir):
    mocker.patch("docker.from_env")
    mocker.patch("time.sleep")

    foodir = tmpdir.mkdir("foo")
    sqlfile = os.path.join(str(foodir), "bar.sql")
    with open(sqlfile, "w") as f:
        f.write("some sql")
    args = (sqlfile, "--data=/some/data")
    parsed_args = cli.Args().parse(*args)
    response = cli.Response()
    backend = DummyDBDockerBackend(parsed_args, response)

    with backend.db():
        assert backend.container.client.containers.run.called
        assert not backend.container.container.stop.called
        assert not backend.container.container.remove.called
    assert backend.container.container.stop.called
    assert backend.container.container.remove.called


def test_backend_base_load_sql(tmpdir):
    foodir = tmpdir.mkdir("foo")
    sqlfile = os.path.join(str(foodir), "bar.sql")
    with open(sqlfile, "w") as f:
        f.write("some sql")
    args = (sqlfile, "--data=/some/data")
    parsed_args = cli.Args().parse(*args)
    response = cli.Response()
    backend = DummyDBDockerBackend(parsed_args, response)

    backend.load_sql(parsed_args.sql_file)
    assert DummyDBDockerBackend.create_db_called is True
    assert (
        DummyDBContainer.sqlfile_called
        == ((parsed_args.db_name, parsed_args.sql_file), ))


def test_backend_base_pipe_sql(tmpdir):
    foodir = tmpdir.mkdir("foo")
    sqlfile = os.path.join(str(foodir), "bar.sql")
    DummyDBContainer.sqlfile_called = None
    with open(sqlfile, "w") as f:
        f.write("some sql")
    args = (sqlfile, "--data=/some/data")
    parsed_args = cli.Args().parse(*args)
    parsed_args.pipeline = [
        "/foo0/bar0.sql", "/foo1/bar1.sql", "/foo2/bar2.sql"]
    response = cli.Response()
    backend = DummyDBDockerBackend(parsed_args, response)
    backend.pipeline_sql()
    pipelines = tuple(
        (parsed_args.db_name,
         "/tmp/pipeline%s/%s"
         % (i, os.path.basename(f)))
        for i, f
        in enumerate(parsed_args.pipeline))
    assert DummyDBContainer.sqlfile_called == pipelines

    parsed_args.pipeline = None
    response = cli.Response()
    backend = DummyDBDockerBackend(parsed_args, response)
    assert backend.pipeline_sql() is None


def test_backend_base_run(tmpdir):

    class Dummy2DBDockerBackend(DBDockerBackend):
        container_class = DummyDBContainer
        called = []

        @contextmanager
        def db(self):
            self.called.append(("db", [], {}))
            yield self

        def load_sql(self, *args, **kwargs):
            self.called.append(("load_sql", args, kwargs))

        def pipeline_sql(self, *args, **kwargs):
            self.called.append(("pipeline_sql", args, kwargs))

        def dump_sql(self, *args, **kwargs):
            self.called.append(("dump_sql", args, kwargs))

    foodir = tmpdir.mkdir("foo")
    sqlfile = os.path.join(str(foodir), "bar.sql")
    with open(sqlfile, "w") as f:
        f.write("some sql")
    args = (sqlfile, "--data=/some/data")
    parsed_args = cli.Args().parse(*args)
    parsed_args.pipeline = [
        "/foo0/bar0.sql", "/foo1/bar1.sql", "/foo2/bar2.sql"]
    response = cli.Response()
    backend = Dummy2DBDockerBackend(parsed_args, response)
    backend.run()
    assert (
        backend.called
        == [('db', [], {}),
            ('load_sql', ('/tmp/sql/bar.sql',), {}),
            ('pipeline_sql', (), {}),
            ('dump_sql', (), {})])
