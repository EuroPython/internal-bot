"""
Configuration for all things discord related
"""
from django.conf import settings

class Roles:
    # We keep this statically defined, because we want to use it in templates
    # for scheduled messages, and we want to make the scheduling available
    # withotu access to the discord server.
    board_member_role_id = settings.DISCORD_BOARD_MEMBER_ROLE_ID
