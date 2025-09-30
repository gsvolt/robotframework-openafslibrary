# Copyright (c) 2025, Sine Nomine Associates
# See LICENSE

import os

from OpenAFSLibrary import logger
from OpenAFSLibrary.variable import get_var
from OpenAFSLibrary.command import pts, kadmin


class _UserKeywords:
    """User keywords."""

    def create_user(
        self,
        name: str,
        id: int,  # =random.randint(9000, 9100),
        gen_keytab: bool = False,
        groups: str = "",
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
        if name in out:
            raise AssertionError(f"Cannot add principal {name} as it already exists")

        # add principal (kadmin -p admin@EXAMPLE.COM -k -t admin.keytab addprinc <name>)
        out = kadmin(
            "-p",
            f"{admin_user}@{krb_realm}",
            "-k",
            "-t",
            admin_keytab,
            "addprinc",
            "-randkey",
            name,
        )

        # create user in openafs (pts createuser -name <name> -id <id>)
        pts("createuser", "-name", name, "-id", id)
        # need to get admin token prior to listprinc

        if not gen_keytab:
            # generate a keytab if requested
            pass

        if groups.strip() != "":
            for group in groups.split(","):
                all_groups = pts("listentries", "-groups")
                if group not in all_groups:
                    pts("creategroup", group)
                pts("adduser", "-user", name, "-group", group)
                logger.info(f"Added {name} to {group}.")

        logger.info("END: User create.")

    def delete_user(self, name):
        """Removes a given username from any groups and deletes it."""
        out = self.list_membership(name)
        for line in out.splitlines():
            if line.endswith(":"):
                continue
            else:
                pts("removeuser", "-user", name, "-group", line.strip())
                logger.info(f"Removed {name} from {line.strip()}.")
        pts("delete", "-nameorid", name)
        logger.info(f"Deleted {name}.")

    def list_membership(self, member):
        """Get membership details for a given member"""
        return pts("membership", "-nameorid", member)
