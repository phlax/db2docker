
import time

import docker

from db2docker import container
from db2docker import cli


class DummyResponse(cli.Response):

    def __init__(self):
        self._responses = []

    def out(self, message):
        self._responses.append(message)


class DummyClient(object):
    pass


class DummyContainer(container.DBContainer):
    docker_image = "dummy"


def test_container_defaults(mocker):
    mocker.patch("docker.from_env")
    mocker.patch("time.sleep")
    response = DummyResponse()
    ct = DummyContainer(response)
    assert (
        ct.container_name
        == 'dockerdb_container')
    assert (
        ct.db_name
        == 'dockerdb_db')
    assert not docker.from_env.called
    ct.container.client
    assert docker.from_env.called


def test_container_wait(mocker):
    mocker.patch("time.sleep")

    response = DummyResponse()
    ct = DummyContainer(response)

    ct.wait_for_container()
    assert time.sleep.call_args[0][0] == 10
    assert time.sleep.called

    time.sleep.reset_mock()

    ct.wait_for_container(5)
    assert time.sleep.call_args[0][0] == 5
    assert time.sleep.called


def test_container_run(mocker):
    mocker.patch("docker.from_env")

    response = DummyResponse()
    ct = DummyContainer(response)
    ct.run("some code")
    assert ct.container.exec_run.called
    assert (
        ct.container.exec_run.call_args[0][0]
        == "some code")


def test_container_environment(mocker):
    response = DummyResponse()
    ct = DummyContainer(response)

    assert ct.get_environment() == {}


def test_container_logs(mocker):
    mocker.patch("docker.from_env")
    response = DummyResponse()
    ct = DummyContainer(response)

    ct.logs()
    assert ct.container.logs.called


def test_container_rm(mocker):
    mocker.patch("docker.from_env")
    response = DummyResponse()
    ct = DummyContainer(response)

    ct.rm()
    assert ct.container.remove.called


def test_container_stop(mocker):
    mocker.patch("docker.from_env")
    response = DummyResponse()
    ct = DummyContainer(response)

    ct.stop()
    assert ct.container.stop.called


def test_container_start(mocker):
    mocker.patch("docker.from_env")
    mocker.patch("time.sleep")
    response = DummyResponse()
    ct = DummyContainer(response)

    ct.start()
    assert ct.client.containers.run.called
    call_args = ct.client.containers.run.call_args
    assert call_args[0][0] == "dummy"
    assert call_args[1]["environment"] == {}
    assert call_args[1]["name"] == "dockerdb_container"
    assert call_args[1]["detach"] is True

    assert time.sleep.called
    assert time.sleep.call_args[0][0] == 10


def test_container_kwargs():
    response = DummyResponse()
    ct = DummyContainer(response)
    kwargs = ct.get_container_kwargs()
    assert kwargs['detach'] is True
    assert kwargs['name'] == ct.container_name
    assert kwargs['environment'] == {}
    assert "volumes" not in kwargs


def test_container_volumes():
    response = DummyResponse()
    volumes = dict(v1=None, v2=None)
    ct = DummyContainer(response, volumes=volumes)
    assert ct.volumes == volumes
    kwargs = ct.get_container_kwargs()
    assert kwargs["volumes"] == volumes
