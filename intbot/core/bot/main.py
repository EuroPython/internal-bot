import discord
from django.conf import settings
from discord.ext import commands

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
async def version(ctx):
    app_version = settings.APP_VERSION
    await ctx.send(f"Version: {app_version}")


def run_bot():
    bot_token = settings.DISCORD_BOT_TOKEN
    bot.run(bot_token)
