
import os

import pytest

from db2docker.cli import Args


def test_cli_args_empty(capsys):
    cliargs = Args()
    capsys.readouterr()

    with pytest.raises(SystemExit):
        cliargs.parse()

    out, err = capsys.readouterr()
    assert (
        "the following arguments are required: sql_file"
        in err)


def test_cli_args_sql_missing_file(capsys):
    cliargs = Args()
    capsys.readouterr()

    args = "foo.sql --data=data"

    with pytest.raises(SystemExit):
        cliargs.parse(*args.split(" "))

    out, err = capsys.readouterr()
    assert (
        "error: Missing SQL file: foo.sql"
        in err)


def test_cli_args_sql_success(capsys, tmpdir):
    args = "%s --data=data"

    cliargs = Args()
    foodir = tmpdir.mkdir("foo")
    sqlfile = os.path.join(str(foodir), "bar.sql")

    with open(sqlfile, "w") as f:
        f.write("some sql")

    result = cliargs.parse(*(args % sqlfile).split(" "))
    assert result.sql_file == sqlfile

    with pytest.raises(SystemExit):
        cliargs.parse(*(args % os.path.basename(sqlfile)).split(" "))

    os.chdir(os.path.dirname(sqlfile))
    cliargs.parse(*(args % os.path.basename(sqlfile)).split(" "))
    assert result.sql_file == sqlfile
    cliargs.parse(*(args % ("./%s" % os.path.basename(sqlfile))).split(" "))
    assert result.sql_file == sqlfile


def test_cli_args_sql_pipe(capsys, tmpdir):
    args = "%s --data=%s" % ("%s", str(tmpdir.mkdir("data")))
    pipes = tmpdir.mkdir("pipe")
    cliargs = Args()
    foodir = tmpdir.mkdir("foo")
    sqlfile = os.path.join(str(foodir), "bar.sql")
    pipe1 = "%s/p1.sql" % pipes

    with open(sqlfile, "w") as f:
        f.write("some sql")
    with open(pipe1, "w") as f:
        f.write("some sql")

    args = "%s --pipe=%s" % ((args % sqlfile), pipe1)
    result = cliargs.parse(*args.split(" "))
    assert result.pipeline == [pipe1]
