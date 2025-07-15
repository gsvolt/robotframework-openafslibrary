# Copyright (c) 2025, Sine Nomine Associates
# See LICENSE

import pytest

from OpenAFSLibrary.keywords.command import _CommandKeywords

keywords = _CommandKeywords()


def test_command_should_succeed_on_ok(process, logged):
    process(code=0, stdout="success")
    keywords.command_should_succeed("command")
    assert "Output: success" in logged.info


def test_command_should_succeed_on_failed(process, logged):
    process(code=1, stderr="failed")
    with pytest.raises(AssertionError):
        keywords.command_should_succeed("command")
    assert "Error: failed" in logged.info


def test_command_should_fail_on_ok(process, logged):
    process(code=0, stdout="success")
    with pytest.raises(AssertionError) as e:
        keywords.command_should_fail("command")
    assert "Command should have failed" in str(e.value)


def test_command_should_fail_on_failed(process, logged):
    process(code=1, stderr="failed")
    keywords.command_should_fail("command")
    assert "Code: 1" in logged.info
