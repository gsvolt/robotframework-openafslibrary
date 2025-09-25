# Copyright (c) 2025, Sine Nomine Associates
# See LICENSE

import pytest
import os
import sys

from OpenAFSLibrary.keywords.user import _UserKeywords


@pytest.fixture
def keywords():
    return _UserKeywords()


krb_realm = "EXAMPLE.COM"
admin_user = "admin"
admin_keytab = "admin.keytab"


def test_create_user__creates_user__when__user_name_is_given(keywords, process):

    user_name = "test_user"
    user_id = "9101"

    process(
        expected_args=[
            "kadmin",
            "-p",
            f"{admin_user}@{krb_realm}",
            "-k",
            "-t",
            f"{admin_keytab}",
            "listprincs",
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
        ],
    )

    process(
        expected_args=[
            "kadmin",
            "-p",
            f"{admin_user}@{krb_realm}",
            "-k",
            "-t",
            admin_keytab,
            "addprinc",
            "-randkey",
            user_name,
        ],
        stdout=[],
    )

    process(
        expected_args=["pts", "createuser", "-name", user_name, "-id", user_id],
        stdout=[],
    )

    keywords.create_user(user_name, user_id)


def test_create_user__fails__when__user_exists(keywords, process):
    user_name = "test_user"
    user_pw = "test_user_pw"
    user_id = "9101"

    process(
        expected_args=[
            "kadmin",
            "-p",
            f"{admin_user}@{krb_realm}",
            "-k",
            "-t",
            f"{admin_keytab}",
            "listprincs",
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
            f"{user_name}@{krb_realm}",
        ],
    )

    process(
        expected_args=[
            "kadmin",
            "-p",
            f"{admin_user}@{krb_realm}",
            "-k",
            "-t",
            admin_keytab,
            "addprinc",
            "-pw",
            user_pw,
            user_name,
        ],
        stdout=[
            f'add_principal: Principal or policy already exists while creating "{user_name}@{krb_realm}".'
        ],
    )

    process(
        expected_args=["pts", "createuser", "-name", user_name, "-id", user_id],
        stdout=[],
    )

    with pytest.raises(AssertionError) as e:
        keywords.create_user(user_name, user_id)


def test_delete_user__succeeds__when__user_name_provided():
    pass
