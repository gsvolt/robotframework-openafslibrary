# Copyright (c) 2025, Sine Nomine Associates
# See LICENSE

import pytest
import os
import sys

from OpenAFSLibrary.keywords.user import(
    _UserKeywords
)

@pytest.fixture
def keywords():
    return _UserKeywords()

def test_create_user__creates_user__when__user_name_is_given(keywords, process):

    krb_realm = "EXAMPLE.COM"
    admin_user = "admin"
    admin_keytab = "admin.keytab"
    user_name = "test_user"
    user_id = ""

    process(
        expected_args = [
            "kadmin",
            "-p",
            f"{admin_user}@{krb_realm}",
            "-k",
            "-t",
            f"{admin_keytab}",
            "listprincs"
        ],
        stdout=[
            "K/M@EXAMPLE.COM",
            "admin@EXAMPLE.COM",
            "afs/example.com@EXAMPLE.COM",
            "kadmin/admin@EXAMPLE.COM",
            "kadmin/changepw@EXAMPLE.COM",
            "krbtgt/EXAMPLE.COM@EXAMPLE.COM",
            "robot@EXAMPLE.COM",
            "root/admin@EXAMPLE.COM",
        ]
    )
    got = keywords.create_user(user_name)
    assert got == ""