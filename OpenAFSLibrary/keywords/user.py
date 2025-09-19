import os
import random

from OpenAFSLibrary import logger
from OpenAFSLibrary import acl
from OpenAFSLibrary import get_var
from OpenAFSLibrary.command import pts, kadmin


class _UserKeywords:
    """User keywords."""

    def create_user(self, user_name, user_id=random.randint(9000, 9100), gen_keytab=False, add_to_group=None):
        """Create an OpenAFS user.

        - create a user principle and AFS pts user account
        - optionally generate a keytab
        - optionally add the user to a group
        """

        logger.info("BEGIN: User create.")

        kadmin = get_var("KADMIN")
        krb_realm = get_var("KRB_REALM")
        admin_user = get_var("KRB_ADMIN_USER")
        admin_keytab = get_var("KRB_ADMIN_KEYTAB")
        user_pw = user_name

        # check if principal exists (kadmin -p admin@EXAMPLE.COM -k -t admin.keytab listprincs)
        out = kadmin("-p", f"{admin_user}@{krb_realm}", "-k", "-t", admin_keytab, "listprincs")
        logger.info(out)
        print(out)

        if "user_name" in out:
            print("Cannot add principal as it already exists: %s" % user_name)
            return

        # add principal (kadmin -p admin@EXAMPLE.COM -k -t admin.keytab addprinc <user_name>)
        out = kadmin("-p", f"{admin_user}@{krb_realm}", "-k", "-t", admin_keytab, "addprinc", "-pw", user_pw, user_name)
        logger.info(out)
        print(out)

        # create user in openafs (pts createuser -name <user_name> -id <user_id>)
        pts("createuser", "-name", user_name, "-id", user_id)

        # need to get admin token prior to listprin

        logger.info("END: User create.")
    
    def delete_user(self, user_name):
        """ delete_user """
        pts("removeuser", "-user", user_name)
    
    def list_users(self):
        """ list_users """
        return pts("listentries", "-users")
