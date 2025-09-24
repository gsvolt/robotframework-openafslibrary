# Copyright (c) 2025, Sine Nomine Associates
# See LICENSE

import pytest
import os
import sys

from OpenAFSLibrary.keywords.group import _GroupKeywords


@pytest.fixture
def keywords():
    return _GroupKeywords()


group_name = "test_group"


def test_create_group__creates_group__when__group_name_is_given(keywords, process):

    process(
        expected_args=["pts", "creategroup", "-name", group_name],
        stdout=["group contract has id -210"],
    )
    keywords.create_group(group_name)


def test_delete_group__deletes_group__when__group_name_is_given(keywords, process):
    process(expected_args=["pts", "delete", "-nameorid", group_name], stdout=[])

    keywords.delete_group(group_name)
