"""
Integrated tests for the Discord Channel Router
"""

from core.bot.channel_router import Channels, discord_channel_router, dont_send_it
from core.models import Webhook


class TestDiscordChannelRouter:
    def test_it_doesnt_send_unkown_messages(self):
        wh = Webhook(source="unkown")
        channel = discord_channel_router(wh)
        assert channel == dont_send_it

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

    def test_it_routes_zammad_billing_queue_to_billing_channel(self):
        wh = Webhook(
            source="zammad",
            meta={},
            content={},
            extra={
                "group": "TestZammad Billing",
            },
        )

        channel = discord_channel_router(wh)

        assert channel == Channels.billing_channel
        assert channel.channel_name == "billing_channel"
        assert channel.channel_id == "123999"

    def test_it_routes_zammad_helpdesk_queue_to_helpdesk_channel(self):
        wh = Webhook(
            source="zammad",
            meta={},
            content={},
            extra={
                "group": "TestZammad Helpdesk",
            },
        )

        channel = discord_channel_router(wh)

        assert channel == Channels.helpdesk_channel
        assert channel.channel_name == "helpdesk_channel"
        assert channel.channel_id == "1237777"

    def test_it_skips_unkown_zammad_groups(self):
        wh = Webhook(
            source="zammad",
            meta={},
            content={},
            extra={
                "group": "Unkown Random Group",
            },
        )

        channel = discord_channel_router(wh)

        assert channel == dont_send_it
