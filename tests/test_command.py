# Copyright (c) 2025, Sine Nomine Associates
# See LICENSE

import pytest
import os
from OpenAFSLibrary.command import (
    run_program,
    rxdebug,
    bos,
    vos,
    fs,
    CommandFailed,
    NoSuchEntryError,
)


def test_run_program(logged):
    rc, out, err = run_program(["echo", "-n", "hello", "world"])
    assert rc == 0
    assert out == "hello world"
    assert err == ""
    assert len(logged.info) == 1
    assert logged.info[0] == "running: echo -n hello world"


def test_run_failing_program(logged):
    rc, out, err = run_program(["false"])
    assert logged.info[0] == "running: false"
    assert rc == 1


def test_run_missing_program(logged, tmp_path):
    missing_path = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        rc, out, err = run_program([missing_path])


def test_run_no_x_program(logged, tmp_path):
    script_path = tmp_path / "no-exec.sh"
    script_path.write_text("#!/bin/sh\necho test\n")
    os.chmod(script_path, 0o644)
    with pytest.raises(PermissionError):
        rc, out, err = run_program([script_path])


def test_run_rxdebug(logged, process):
    process(stdout="Usage: rxdebug -servers ...")
    out = rxdebug("-help")
    assert out.startswith("Usage:")
    assert len(logged.info) == 1
    assert logged.info[0] == "running: rxdebug -help"


def test_run_vos(logged, process):
    process(stdout="vos: Commands are: ...")
    out = vos("help")
    assert out.startswith("vos: Commands are:")
    assert len(logged.info) == 1
    assert logged.info[0] == "running: vos help"


def test_run_vos_bad_subcommand(logged, process):
    process(code=255, stdout="vos: Unrecognized operation")
    with pytest.raises(CommandFailed):
        vos("bogus")


def test_run_vos_no_such_entry_error(logged, process):
    process(code=255, stderr="error\nVLDB: no such entry")
    with pytest.raises(NoSuchEntryError):
        vos("bogus")


def test_run_vos_no_exists_error(logged, process):
    process(code=255, stderr="error\ndoes not exist")
    with pytest.raises(NoSuchEntryError):
        vos("bogus")


def test_run_bos(logged, process):
    process(stdout="bos: Commands are: ...")
    out = bos("help")
    assert out.startswith("bos: Commands are:")
    assert len(logged.info) == 1
    assert logged.info[0] == "running: bos help"


def test_run_fs(logged, process):
    process(stdout="fs: Commands are: ...")
    out = fs("help")
    assert out.startswith("fs: Commands are:")
    assert len(logged.info) == 1
    assert logged.info[0] == "running: fs help"


def test_run_custom_path_fs(logged, process, variables):
    variables["FS"] = "/my/custom/path/fs"
    process(stdout="fs: Commands are: ...")
    out = fs("help")
    assert out.startswith("fs: Commands are:")
    assert len(logged.info) == 1
    assert logged.info[0] == "running: /my/custom/path/fs help"
