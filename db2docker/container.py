
import time

import docker


class DBContainer(object):

    def __init__(self, response, **kwargs):
        self.response = response
        self.container_name = kwargs.get(
            "container_name", "dockerdb_container")
        self.db_name = kwargs.get(
            "db_name", "dockerdb_db")
        self.volumes = kwargs.get("volumes")

    @property
    def client(self):
        return docker.from_env()

    @property
    def container(self):
        return self.client.containers.get(
            self.container_name)

    def run(self, command):
        self.response.out("> Running command: %s" % command)
        result = self.container.exec_run(command)
        self.response.out("> Command completed")
        return result.decode()

    def get_environment(self):
        return {}

    def get_container_kwargs(self):
        kwargs = dict(
            name=self.container_name,
            environment=self.get_environment(),
            detach=True)
        if self.volumes:
            kwargs["volumes"] = self.volumes
        return kwargs

    def logs(self):
        return self.container.logs()

    def rm(self):
        self.response.out(
            "> Removing %s db container"
            % self.docker_image)
        self.container.remove()
        self.response.out(
            "> DB (%s) container removed"
            % self.docker_image)

    def start(self):
        self.response.out(
            "> Starting %s db container..."
            % self.docker_image)
        self.client.containers.run(
            self.docker_image,
            **self.get_container_kwargs())
        self.wait_for_container()
        self.response.out(
            "> DB (%s) container started"
            % self.docker_image)

    def stop(self):
        self.response.out(
            "> Stopping %s db container..."
            % self.docker_image)
        self.container.stop()
        self.response.out(
            "> DB (%s) container stopped"
            % self.docker_image)

    def wait_for_container(self, wait=10):
        time.sleep(wait)
