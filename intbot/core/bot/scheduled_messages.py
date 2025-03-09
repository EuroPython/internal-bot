"""
Factory functions for scheduled messages
"""

from typing import Dict, Callable

from django.utils import timezone

from core.models import DiscordMessage
from core.bot.channel_router import Channels


def standup_message_factory() -> DiscordMessage:
    """Factory for weekly standup message."""
    today = timezone.now()
    week_number = today.isocalendar()[1]
    
    content = (
        f"## Monday Standup - Week {week_number}\n\n"
        f"Good morning team! Please share:\n\n"
        f"1. What you accomplished last week\n"
        f"2. What you're planning for this week\n"
        f"3. Any blockers or assistance needed"
    )
    
    # Using the test channel for now - replace with appropriate channel later
    channel = Channels.test_channel
    
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