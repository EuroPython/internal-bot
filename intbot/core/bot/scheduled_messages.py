"""
Factory functions for scheduled messages
"""

from typing import Dict, Callable

from core.models import DiscordMessage
from core.bot.channel_router import Channels
from core.bot.config import Roles


def standup_message_factory() -> DiscordMessage:
    """Factory for weekly standup message."""
    content = (
        f"## Happy Monday <@&{Roles.board_member_role_id}>!\n\n"
        f"Let's keep everyone in the loop :)\n\n"
        f"(1) What you worked on last week\n"
        f"(2) What are you planning to work on this week\n"
        f"(3) Are there any blockers or where could you use some help?"
    )
    
    # Using the test channel for now - replace with appropriate channel later
    channel = Channels.standup_channel
    
    return DiscordMessage(
        channel_id=channel.channel_id,
        channel_name=channel.channel_name,
        content=content,
        sent_at=None
    )


# Registry of message factories
MESSAGE_FACTORIES: Dict[str, Callable[[], DiscordMessage]] = {
    "standup": standup_message_factory,
}
