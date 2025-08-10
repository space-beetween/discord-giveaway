import asyncio

import disnake
from disnake.ext import commands
from loguru import logger

from . import models
from .giveaway_manager import GiveawayManager
from .config import Config
from .ui import GiveawayView


_conf = Config()

intents = disnake.Intents(
    guilds=True,
    members=True,
)
test_guilds = _conf.test_guilds if _conf.test_guilds else None
bot = commands.InteractionBot(test_guilds=test_guilds, intents=intents)
bot.load_extensions("src/cogs")


@bot.event
async def on_ready():
    logger.info("ready")


async def setup():
    await models.setup()
    bot.add_view(GiveawayView(GiveawayManager(bot)))


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    bot.run(_conf.token)
