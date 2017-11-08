import os

from db2docker.backends.mariadb import (
    MariaDBContainer, MariaDBDockerBackend)
from db2docker import cli


def test_backend_mariadb_defaults(tmpdir):
    foodir = tmpdir.mkdir("foo")
    sqlfile = os.path.join(str(foodir), "bar.sql")
    with open(sqlfile, "w") as f:
        f.write("some sql")
    args = (sqlfile, "--data=/some/data")
    parsed_args = cli.Args().parse(*args)

    response = cli.Response()
    backend = MariaDBDockerBackend(parsed_args, response)
    assert backend.args == parsed_args
    assert backend.response == response
    assert backend.container_class == MariaDBContainer
    assert isinstance(
        backend.container,
        backend.container_class)
    assert backend.container.response == response
    assert backend.container.container_name == parsed_args.container_name
    assert backend.container.db_name == parsed_args.db_name
    assert backend.volumes == backend.container.volumes


def test_backend_mariadb_container(mocker, tmpdir):
    mocker.patch("docker.from_env")
    foodir = tmpdir.mkdir("foo")
    sqlfile = os.path.join(str(foodir), "bar.sql")
    with open(sqlfile, "w") as f:
        f.write("some sql")
    args = (sqlfile, "--data=/some/data")
    parsed_args = cli.Args().parse(*args)

    response = cli.Response()
    backend = MariaDBDockerBackend(parsed_args, response)
    assert(
        backend.container.docker_image
        == 'mariadb')
    assert (
        backend.container.get_environment()
        == {'MYSQL_ALLOW_EMPTY_PASSWORD': 'yes'})
    ct = backend.container
    ct.sql("show databases")
    assert backend.container.container.exec_run.called
    assert (
        backend.container.container.exec_run.call_args[0][0]
        == 'mysql -e "show databases"')


def test_backend_mariadb_create_db(mocker, tmpdir):
    mocker.patch("docker.from_env")
    foodir = tmpdir.mkdir("foo")
    sqlfile = os.path.join(str(foodir), "bar.sql")
    with open(sqlfile, "w") as f:
        f.write("some sql")
    args = (sqlfile, "--data=/some/data")
    parsed_args = cli.Args().parse(*args)

    response = cli.Response()
    backend = MariaDBDockerBackend(parsed_args, response)
    backend.create_db()
    assert(
        backend.container.container.exec_run.call_args[0][0]
        == ('mysql -e "CREATE DATABASE dockerdb CHARACTER SET utf8 '
            'DEFAULT COLLATE utf8_general_ci;"'))


def test_backend_mariadb_dump_db(mocker, tmpdir):
    mocker.patch("docker.from_env")
    foodir = tmpdir.mkdir("foo")
    sqlfile = os.path.join(str(foodir), "bar.sql")
    with open(sqlfile, "w") as f:
        f.write("some sql")
    args = (sqlfile, "--out=/some/data.sql")
    parsed_args = cli.Args().parse(*args)
    response = cli.Response()
    backend = MariaDBDockerBackend(parsed_args, response)
    backend.dump_sql()
    assert(
        backend.container.container.exec_run.call_args[0][0]
        == ("sh -c 'mysqldump dockerdb > /tmp/out/data.sql'"))

    args = (sqlfile, "--data=/some/data")
    parsed_args = cli.Args().parse(*args)
    response = cli.Response()
    backend = MariaDBDockerBackend(parsed_args, response)
    assert backend.dump_sql() is None
