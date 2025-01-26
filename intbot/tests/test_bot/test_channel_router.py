"""
Integrated tests for the Discord Channel Router
"""

from core.bot.channel_router import Channels, discord_channel_router
from core.models import Webhook


class TestDiscordChannelRouter:
    def test_it_routes_board_project_to_board_channel(self):
        wh = Webhook(
            source="github",
            meta={"X-Github-Event": "projects_v2_item"},
            content={},
            extra={
                "project": {
                    "id": "PVT_Test_Board_Project",
                    "title": "Board Project",
                    "url": "https://github.com/europython",
                },
            },
        )

        channel = discord_channel_router(wh)

        assert channel == Channels.board_channel
        assert channel.channel_name == "board_channel"
        assert channel.channel_id == "1234567"

    def test_it_routes_ep2025_project_to_ep2025_channel(self):
        wh = Webhook(
            source="github",
            meta={"X-Github-Event": "projects_v2_item"},
            content={},
            extra={
                "project": {
                    "id": "PVT_Test_ep2025_Project",
                    "title": "EP2025 Project",
                    "url": "https://github.com/europython",
                },
            },
        )

        channel = discord_channel_router(wh)

        assert channel == Channels.ep2025_channel
        assert channel.channel_name == "ep2025_channel"
        assert channel.channel_id == "1232025"

    def test_it_routes_EM_project_to_EM_channel(self):
        wh = Webhook(
            source="github",
            meta={"X-Github-Event": "projects_v2_item"},
            content={},
            extra={
                "project": {
                    "id": "PVT_Test_EM_Project",
                    "title": "EM Project",
                    "url": "https://github.com/europython",
                },
            },
        )

        channel = discord_channel_router(wh)

        assert channel == Channels.em_channel
        assert channel.channel_name == "em_channel"
        assert channel.channel_id == "123123"
