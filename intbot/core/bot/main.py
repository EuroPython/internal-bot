import io

import discord
from asgiref.sync import sync_to_async
from core.analysis.products import latest_flat_product_data
from core.analysis.submissions import (
    group_submissions_by_state,
    latest_flat_submissions_data,
    piechart_submissions_by_state,
)
from core.models import DiscordMessage, InboxItem
from discord.ext import commands, tasks
from django.conf import settings
from django.utils import timezone

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Inbox emoji used for adding messages to user's inbox
INBOX_EMOJI = "📥"


@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")
    poll_database.start()  # Start polling the database


@bot.event
async def on_raw_reaction_add(payload):
    """Handle adding messages to inbox when users react with the inbox emoji"""
    if payload.emoji.name == INBOX_EMOJI:
        # Get the channel and message details
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        # Create a new inbox item using async
        await InboxItem.objects.acreate(
            message_id=str(message.id),
            channel_id=str(payload.channel_id),
            channel_name=f"#{channel.name}",
            server_id=str(payload.guild_id),
            user_id=str(payload.user_id),
            author=str(message.author.name),
            content=message.content,
        )


@bot.event
async def on_raw_reaction_remove(payload):
    """Handle removing messages from inbox when users remove the inbox emoji"""
    if payload.emoji.name == INBOX_EMOJI:
        # Remove the inbox item
        items = InboxItem.objects.filter(
            message_id=str(payload.message_id),
            user_id=str(payload.user_id),
        )
        await items.adelete()


@bot.command()
async def inbox(ctx):
    """
    Displays the content of the inbox for the user that calls the command.

    Each message is saved with user_id (which is a discord id), and here we can
    filter out all those messages depending on who called the command.

    It retuns all tracked messages, starting from the one most recently saved
    (a message that was most recently tagged with inbox emoji, not the message
    that was most recently sent).
    """
    user_id = str(ctx.message.author.id)
    inbox_items = InboxItem.objects.filter(user_id=user_id).order_by("-created_at")

    # Use async query
    if not await inbox_items.aexists():
        await ctx.send("Your inbox is empty.")
        return

    msg = "Currently tracking the following messages:\n"

    async for item in inbox_items:
        msg += "* " + item.summary() + "\n"

    # Create an embed to display the inbox
    embed = discord.Embed()
    embed.description = msg
    await ctx.send(embed=embed)


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.command()
async def source(ctx):
    await ctx.send(
        "I'm here: https://github.com/europython/internal-bot",
        suppress_embeds=True,
    )


@bot.command()
async def wiki(ctx):
    await ctx.send(
        "Please add it to the wiki: "
        "[ep2025-wiki.europython.eu](https://ep2025-wiki.europython.eu)",
        suppress_embeds=True,
    )


@bot.command()
async def close(ctx):
    channel = ctx.channel
    author = ctx.message.author

    # Check if it's a public or private post (thread)
    if channel.type in (
        discord.ChannelType.public_thread,
        discord.ChannelType.private_thread,
    ):
        parent = channel.parent

        # Check if the post (thread) was sent in a forum,
        # so we can add a tag
        if parent.type == discord.ChannelType.forum:
            # Get tag from forum
            tag = None
            for _tag in parent.available_tags:
                if _tag.name.lower() == "done":
                    tag = _tag
                    break

            if tag is not None:
                await channel.add_tags(tag)

        # Remove command message
        await ctx.message.delete()

        # Send notification to the thread
        await channel.send(
            f"# This was marked as done by {author.mention}", suppress_embeds=True
        )

        # We need to archive after adding tags in case it was a forum.
        await channel.edit(archived=True)
    else:
        # Remove command message
        await ctx.message.delete()

        await channel.send(
            "The !close command is intended to be used inside a thread/post",
            suppress_embeds=True,
            delete_after=5,
        )


@bot.command()
async def version(ctx):
    app_version = settings.APP_VERSION
    await ctx.send(f"Version: {app_version}")


@bot.command()
async def qlen(ctx):
    qs = get_messages()
    # qs = DiscordMessage.objects.afilter(sent_at__isnull=True)
    cnt = await qs.acount()
    await ctx.send(f"In the queue there are: {cnt} messages")


def get_messages():
    messages = DiscordMessage.objects.filter(sent_at__isnull=True)
    return messages


@tasks.loop(seconds=60)  # Seconds
async def poll_database():
    """Check for unsent messages and send them."""
    messages = get_messages()
    print("Polling database.... ", timezone.now())

    async for message in messages:
        channel = bot.get_channel(int(message.channel_id))
        if channel:
            await channel.send(
                message.content,
                suppress_embeds=True,
            )
            message.sent_at = timezone.now()
            await message.asave()
        else:
            print("Channel does not exist!")


@bot.command()
async def until(ctx):
    """
    Returns time left until the conference
    """
    delta = settings.CONFERENCE_START - timezone.now()

    await ctx.send(f"{delta.days} days left until the conference")


@bot.command()
@commands.has_role("EP2025")
async def products(ctx):
    """
    Returns pretix Products but only if called by a EP2025 volunteer on a test channel.

    This is an example of implementation of a command that has some basic
    access control (in this case works only on certain channels).
    """

    if ctx.channel.id != settings.DISCORD_TEST_CHANNEL_ID:
        await ctx.send("This command only works on certain channels")
        return

    data = await sync_to_async(latest_flat_product_data)()

    await ctx.send(f"```{str(data)}```")


@bot.command()
async def submissions_status(ctx):
    df = await sync_to_async(latest_flat_submissions_data)()
    by_state = group_submissions_by_state(df)

    await ctx.send(f"```{str(by_state)}```")


@bot.command()
async def submissions_status_pie_chart(ctx):
    df = await sync_to_async(latest_flat_submissions_data)()
    by_state = group_submissions_by_state(df)
    piechart = piechart_submissions_by_state(by_state)

    png_bytes = piechart.to_image(format="png")
    file = discord.File(io.BytesIO(png_bytes), filename="submissions_by_state.png")

    await ctx.send(file=file)


def run_bot():
    bot_token = settings.DISCORD_BOT_TOKEN
    bot.run(bot_token)
