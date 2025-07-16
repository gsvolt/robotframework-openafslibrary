# Copyright (c) 2025, Sine Nomine Associates
# See LICENSE

import pytest
from OpenAFSLibrary.keywords.dump import (
    VolumeDump,
    _DumpKeywords,
)

keywords = _DumpKeywords()

#
# VolumeDump helper class tests.
#


def test_create_dump_file(tmp_path):
    filename = tmp_path / "test.dump"
    VolumeDump(filename)
    assert filename.exists()


#
# Keyword tests.
#


def test_should_be_a_dump_file(tmp_path):
    filename = tmp_path / "test.dump"
    # TODO: Copy test file to tmp dir.
    keywords.create_dump(filename, size="small")
    assert filename.exists()
    keywords.should_be_a_dump_file(filename)


def test_create_dump_with_bogus_acl(tmp_path):
    filename = tmp_path / "test.dump"
    keywords.create_dump(filename, size="small", contains="bogus-acl")
    assert filename.exists()


def test_create_dump_empty(tmp_path):
    filename = tmp_path / "test.dump"
    keywords.create_dump(filename, size="empty")
    assert filename.exists()


def test_create_dump_small(tmp_path):
    filename = tmp_path / "test.dump"
    keywords.create_dump(filename, size="small")
    assert filename.exists()


def test_create_dump_invalid_size_asserts(tmp_path):
    filename = tmp_path / "test.dump"
    with pytest.raises(ValueError):
        keywords.create_dump(filename, size="bogus")
    assert not filename.exists()
