import os

import pytest

from db2docker.backends.base import DBDockerBackend
from db2docker.db2d import db2d


class DummyDBDockerBackend(DBDockerBackend):

    called = False

    def run(self):
        DummyDBDockerBackend.called = True


def test_db2d(mocker, tmpdir):
    assert list(db2d.types.keys()) == ["mariadb"]

    db2d.register("dummy", DummyDBDockerBackend)
    assert sorted(db2d.types.keys()) == ["dummy", "mariadb"]

    foodir = tmpdir.mkdir("foo")
    sqlfile = os.path.join(str(foodir), "bar.sql")

    with open(sqlfile, "w") as f:
        f.write("some sql")
    db2d.run(sqlfile, "--container-type=dummy", "--data=/some/data")
    assert DummyDBDockerBackend.called is True

    with pytest.raises(SystemExit):
        db2d.run(sqlfile, "--container-type=DOESNOTEXIST", "--data=/some/data")
