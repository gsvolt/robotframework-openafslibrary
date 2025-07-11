# Copyright (c) 2025, Sine Nomine Associates
# See LICENSE

import pytest
import os
from OpenAFSLibrary.command import run_program


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
