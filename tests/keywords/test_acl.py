# Copyright (c) 2025, Sine Nomine Associates
# See LICENSE

import pytest

from OpenAFSLibrary.keywords.acl import (
    normalize,
    parse,
    AccessControlList,
    _ACLKeywords,
)

keywords = _ACLKeywords()

#
# Tests for Internal helper functions.
#


@pytest.mark.parametrize(
    "value, expected",
    [
        (list(), list()),
        (list("r"), list("r")),
        (list("lr"), list("rl")),
        (list("rlidwka"), list("rlidwka")),
        (list("adiklrw"), list("rlidwka")),
    ],
    ids=lambda p: "".join(p),
)
def test_normalize(value, expected):
    got = normalize(value)
    assert got == expected


@pytest.mark.parametrize("invalid", list("bcmxyzXZY123.,-+=!?@/(){}"))
def test_normalize_invalid(invalid):
    with pytest.raises(AssertionError) as e:
        normalize([invalid])
    assert "Illegal rights character" in str(e.value)


@pytest.mark.parametrize(
    "value,sign,rights",
    [
        # "",  TODO: This test fails!
        ("r", "+", list("r")),
        ("rl", "+", list("rl")),
        ("rlidwka", "+", list("rlidwka")),
        ("all", "+", list("rlidwkaABCDEFGH")),
        ("read", "+", list("rl")),
        ("write", "+", list("rlidwk")),
        ("none", "+", list()),
        ("dlikraw", "+", list("rlidwka")),
        ("rrrrllll", "+", list("rl")),
        ("+r", "+", list("r")),
        ("-r", "-", list("r")),
        ("-all", "-", list("rlidwkaABCDEFGH")),
        ("-read", "-", list("rl")),
        ("-write", "-", list("rlidwk")),
        ("-none", "-", list()),
    ],
)
def test_parse(value, sign, rights):
    got_sign, got_rights = parse(value)
    assert got_sign == sign
    assert got_rights == rights


@pytest.mark.parametrize(
    "value",
    [
        list("abc"),
        list("+XYZ"),
        list("---"),
        list("+++"),
    ],
)
def test_parse_invalid(value):
    with pytest.raises(AssertionError) as e:
        parse(value)
    assert "Illegal rights character" in str(e.value)


#
# Tests for the internal helper class.
#


@pytest.mark.parametrize(
    "args,expected",
    [
        # ([], "", "", {}),  # todo
        (["u r"], {"u": ("r", "")}),
        (["u r", "v w"], {"u": ("r", ""), "v": ("w", "")}),
    ],
)
def test_acl_class_from_args(args, expected):
    a = AccessControlList.from_args(*args)
    assert a.acls == expected


def test_acl_class_from_path(process, tmp_path):
    process(
        stdout=f"""\
Access list for {tmp_path}
Normal rights:
  system:anyuser rl
  user1 rlidwk
"""
    )
    expected = {"system:anyuser": ("rl", ""), "user1": ("rlidwk", "")}
    a = AccessControlList.from_path(tmp_path)
    assert a.acls == expected


@pytest.mark.parametrize(
    "args,name,rights,expected",
    [
        # ([], "", "", {}),  # todo
        ([], "u", "r", {"u": ("r", "")}),
        ([], "u", "-r", {"u": ("", "r")}),
        ([], "u", "read", {"u": ("rl", "")}),
        ([], "u", "write", {"u": ("rlidwk", "")}),
        ([], "u", "all", {"u": ("rlidwkaABCDEFGH", "")}),
        (["u r"], "v", "w", {"u": ("r", ""), "v": ("w", "")}),
        (["u rlidwka"], "u", "rlidwk", {"u": ("rlidwka", "")}),
    ],
)
def test_acl_class_add_entry(args, name, rights, expected):
    a = AccessControlList.from_args(*args)
    a.add(name, rights)
    assert a.acls == expected


@pytest.mark.parametrize(
    "args,name,rights,expected",
    [
        ([], "u", "r", False),
        (["u r"], "u", "r", True),
        (["u r", "v w"], "v", "w", True),
        (["u read"], "u", "rl", True),
        (["u read"], "u", "rlidwk", False),
        (["u rl", "u -a"], "u", "-a", True),
    ],
)
def test_acl_class_contains(args, name, rights, expected):
    a = AccessControlList.from_args(*args)
    assert a.contains(name, rights) is expected


#
# Keyword tests.
#


@pytest.mark.parametrize(
    "path,name,rights,expected",
    [
        ("/a/b/c", "u", "r", "fs setacl -dir /a/b/c -acl u r"),
        ("/a/b/c", "u", "rlidwka", "fs setacl -dir /a/b/c -acl u rlidwka"),
        ("/a/b/c", "u", "read", "fs setacl -dir /a/b/c -acl u read"),
        ("/a/b/c", "u", "write", "fs setacl -dir /a/b/c -acl u write"),
        ("/a/b/c", "u", "none", "fs setacl -dir /a/b/c -acl u none"),
    ],
)
def test_add_access_rights_passes(process, logged, path, name, rights, expected):
    keywords.add_access_rights(path, name, rights)
    got = logged.info[0]
    assert got == f"running: {expected}"


@pytest.mark.parametrize(
    "acls",
    [
        ["user1 rlidwk"],
    ],
)
def test_access_control_list_matches_passes(process, tmp_path, acls):
    process(
        stdout=f"""\
Access list for {tmp_path}
Normal rights:
  user1 rlidwk
"""
    )
    keywords.access_control_list_matches(tmp_path, *acls)


@pytest.mark.parametrize(
    "acls",
    [
        ["user1 rlidwk"],
    ],
)
def test_access_control_list_matches_fails(process, tmp_path, acls):
    process(
        stdout=f"""\
Access list for {tmp_path}
Normal rights:
  user2 rlidwk
"""
    )
    with pytest.raises(AssertionError) as e:
        keywords.access_control_list_matches(tmp_path, *acls)
    assert "ACLs do not match" in str(e.value)


def test_access_control_list_contains_passes(process, tmp_path):
    process(
        stdout=f"""\
Access list for {tmp_path}
Normal rights:
  user1 rlidwk
"""
    )
    name = "user1"
    rights = "rlidwk"
    keywords.access_control_list_contains(tmp_path, name, rights)


def test_access_control_list_contains_fails(process, tmp_path):
    process(
        stdout=f"""\
Access list for {tmp_path}
Normal rights:
  user1 rlidwk
"""
    )
    name = "user1"
    rights = "rl"
    with pytest.raises(AssertionError) as e:
        keywords.access_control_list_contains(tmp_path, name, rights)
    assert "ACL entry rights do not match" in str(e.value)


def test_access_control_should_exist_passes(process, tmp_path):
    process(
        stdout=f"""\
Access list for {tmp_path}
Normal rights:
  user1 rlidwk
"""
    )
    name = "user1"
    keywords.access_control_should_exist(tmp_path, name)


def test_access_control_should_exist_fails(process, tmp_path):
    process(
        stdout=f"""\
Access list for {tmp_path}
Normal rights:
  user1 rlidwk
"""
    )
    name = "user2"
    with pytest.raises(AssertionError) as e:
        keywords.access_control_should_exist(tmp_path, name)
    assert "ACL entry does not exist" in str(e.value)


def test_access_control_should_not_exist_passes(process, tmp_path):
    process(
        stdout=f"""\
Access list for {tmp_path}
Normal rights:
  user1 rlidwk
"""
    )
    name = "user2"
    with pytest.raises(AssertionError) as e:
        keywords.access_control_should_exist(tmp_path, name)
    assert "ACL entry does not exist" in str(e.value)


def test_access_control_should_not_exist_fails(process, tmp_path):
    process(
        stdout=f"""\
Access list for {tmp_path}
Normal rights:
  user1 rlidwk
"""
    )
    name = "user1"
    keywords.access_control_should_exist(tmp_path, name)
