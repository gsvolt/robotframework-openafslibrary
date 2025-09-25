# Copyright (c) 2025, Sine Nomine Associates
# See LICENSE

from OpenAFSLibrary import logger
from OpenAFSLibrary.variable import get_var
from OpenAFSLibrary.command import pts, kadmin


class _UserKeywords:
    """User keywords."""

    def create_user(
        self,
        user_name: str,
        user_id: int,  # =random.randint(9000, 9100),
        gen_keytab: bool = False,
        add_to_group: bool = False,
        group_name: str = "",
    ) -> int:
        """Create an OpenAFS user.
        - create a user principle and AFS pts user account
        - optionally generate a keytab
        - optionally add the user to a group
        """
        logger.info("BEGIN: User create.")
        krb_realm = get_var("KRB_REALM")
        admin_user = get_var("KRB_ADMIN_USER")
        admin_keytab = get_var("KRB_ADMIN_KEYTAB")

        # check if principal exists (kadmin -p admin@EXAMPLE.COM -k -t admin.keytab listprincs)
        out = kadmin(
            "-p", f"{admin_user}@{krb_realm}", "-k", "-t", admin_keytab, "listprincs"
        )
        logger.info(f"out={out}")
        if user_name in out:
            raise AssertionError(
                f"Cannot add principal {user_name} as it already exists"
            )

        # add principal (kadmin -p admin@EXAMPLE.COM -k -t admin.keytab addprinc <user_name>)
        out = kadmin(
            "-p",
            f"{admin_user}@{krb_realm}",
            "-k",
            "-t",
            admin_keytab,
            "addprinc",
            "-randkey",
            user_name,
        )
        logger.info(f"out={out}")
        # create user in openafs (pts createuser -name <user_name> -id <user_id>)
        pts("createuser", "-name", user_name, "-id", user_id)
        # need to get admin token prior to listprinc
        logger.info("END: User create.")

    def delete_user(self, user_name):
        """delete_user"""
        pts("removeuser", "-user", user_name)

    def list_users(self):
        """list_users"""
        return pts("listentries", "-users")
