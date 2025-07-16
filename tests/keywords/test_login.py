# Copyright (c) 2025, Sine Nomine Associates
# See LICENSE

import pytest
from OpenAFSLibrary.keywords.login import (
    get_principal,
    akimpersonate,
    login_with_password,
    login_with_keytab,
    _LoginKeywords,
)

keywords = _LoginKeywords()

#
# Helper function tests.
#


@pytest.mark.parametrize(
    "user,realm,expected",
    [
        ("user", "example.com", "user@example.com"),
        ("user.admin", "example.com", "user/admin@example.com"),
        ("", "example.com", "@example.com"),
        ("user", "", "user@"),
        ("", "", "@"),
    ],
)
def test_get_principal(user, realm, expected):
    got = get_principal(user, realm)
    assert got == expected


def test_akimpersonate_with_defaults(process, logged):
    expected = "aklog -d -c example.com -k EXAMPLE.COM -keytab robot.keytab -principal user@EXAMPLE.COM"
    akimpersonate("user")
    assert logged.info[0] == f"running: {expected}"


def test_akimpersonate_with_vars(process, variables, logged):
    expected = "v1 -d -c v2 -k v3 -keytab v4 -principal user@v3"
    variables["AKLOG"] = "v1"
    variables["AFS_CELL"] = "v2"
    variables["KRB_REALM"] = "v3"
    variables["KRB_AFS_KEYTAB"] = "v4"
    akimpersonate("user")
    assert logged.info[0] == f"running: {expected}"


def test_akimpersonate_fails(process, logged):
    process(code=1, stderr="fail test")
    with pytest.raises(AssertionError) as e:
        akimpersonate("user")
    assert "aklog failed" in str(e.value)


def test_login_with_password_with_defaults(process, logged):
    expected = (
        "klog.krb5 -principal user -password password -cell example.com -k EXAMPLE.COM"
    )
    login_with_password("user", "password")
    assert logged.info[0] == f"running: {expected}"


def test_login_with_password_with_vars(process, variables, logged):
    expected = "v1 -principal user -password password -cell v2 -k v3"
    variables["KLOG_KRB5"] = "v1"
    variables["AFS_CELL"] = "v2"
    variables["KRB_REALM"] = "v3"
    login_with_password("user", "password")
    assert logged.info[0] == f"running: {expected}"


@pytest.mark.parametrize(
    "user,password",
    [
        (None, None),
        ("", ""),
        (None, "password"),
        ("", "password"),
        ("user", None),
        ("user", ""),
    ],
)
def test_login_with_password_missing_argument(process, user, password):
    with pytest.raises(AssertionError) as e:
        login_with_password(user, password)
    assert "is required" in str(e.value)


def test_login_with_keytab_with_defaults(process, logged, tmp_path):
    keytab = tmp_path / "test.keytab"
    keytab.touch()
    expected = [
        f"keytab: {keytab}",
        f"running: kinit -k -t {keytab} user@EXAMPLE.COM",
        f"running: aklog -d -c example.com -k EXAMPLE.COM",
    ]
    login_with_keytab("user", str(keytab))
    assert logged.info[0] == expected[0]
    assert logged.info[1] == expected[1]
    assert logged.info[2] == expected[2]


def test_login_with_keytab_with_vars(process, logged, tmp_path, variables):
    variables["KINIT"] = "v1"
    variables["AKLOG"] = "v2"
    variables["AFS_CELL"] = "v3"
    variables["KRB_REALM"] = "v4"
    keytab = tmp_path / "test.keytab"
    keytab.touch()
    expected = [
        f"keytab: {keytab}",
        f"running: v1 -k -t {keytab} user@v4",
        f"running: v2 -d -c v3 -k v4",
    ]
    login_with_keytab("user", str(keytab))
    assert logged.info[0] == expected[0]
    assert logged.info[1] == expected[1]
    assert logged.info[2] == expected[2]


#
# Keyword tests.
#


def test_login_with_akimpersonate(process, logged, variables):
    expected = "aklog -d -c example.com -k EXAMPLE.COM -keytab robot.keytab -principal user@EXAMPLE.COM"
    variables["AFS_AKIMPERSONATE"] = True
    keywords.login("user")
    assert logged.info[0] == f"running: {expected}"


def test_login_with_password(process, logged):
    expected = (
        "klog.krb5 -principal user -password password -cell example.com -k EXAMPLE.COM"
    )
    keywords.login("user", password="password")
    assert logged.info[0] == f"running: {expected}"


def test_login_with_keytab(process, logged, tmp_path):
    keytab = tmp_path / "test.keytab"
    keytab.touch()
    expected = [
        f"keytab: {keytab}",
        f"running: kinit -k -t {keytab} user@EXAMPLE.COM",
        f"running: aklog -d -c example.com -k EXAMPLE.COM",
    ]
    keywords.login("user", keytab=str(keytab))
    assert logged.info[0] == expected[0]
    assert logged.info[1] == expected[1]
    assert logged.info[2] == expected[2]


def test_login_missing_args(process, logged, tmp_path):
    with pytest.raises(ValueError) as e:
        keywords.login("user")
    assert "password or keytab is required" in str(e.value)


def test_logout_with_defaults(process, logged):
    keywords.logout()
    assert "kdestroy" in logged.info[0]
    assert "unlog" in logged.info[1]


def test_logout_with_vars(process, logged, variables):
    variables["AFS_AKIMPERSONATE"] = False
    variables["KDESTROY"] = "v1"
    variables["UNLOG"] = "v2"
    keywords.logout()
    assert "v1" in logged.info[0]
    assert "v2" in logged.info[1]


def test_logout_in_akimperonate_mode(process, logged, variables):
    variables["AFS_AKIMPERSONATE"] = True
    keywords.logout()
    assert "unlog" in logged.info[0]
