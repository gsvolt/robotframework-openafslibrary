from OpenAFSLibrary import logger
from OpenAFSLibrary.command import pts


class _GroupKeywords:
    """Group keywords."""

    def create_group(self, group_name):
        """Creates an OpenAFS group."""
        pts("creategroup", group_name)

    def remove_group(self, group_name):
        """Removes an OpenAFS group."""
        if len(group_name.strip()) == 0:
            logger.error("empty group name")
            return
        pts("delete", "-nameorid", group_name)

    def list_groups(self):
        return pts("listentries", "-groups")
