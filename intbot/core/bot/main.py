import discord
from core.models import DiscordMessage
from discord.ext import commands, tasks
from django.conf import settings
from django.utils import timezone

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")


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


def run_bot():
    bot_token = settings.DISCORD_BOT_TOKEN
    bot.run(bot_token)
