from OpenAFSLibrary import logger
from OpenAFSLibrary.command import pts


class _GroupKeywords:
    """Group keywords."""

    def create_group(self, group_name):
        """Creates an OpenAFS group."""
        pts("creategroup", "-name", group_name)

    def delete_group(self, group_name):
        """Deletes an OpenAFS group."""
        pts("delete", "-nameorid", group_name)

    def list_groups(self):
        return pts("listentries", "-groups")
