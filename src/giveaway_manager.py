from datetime import datetime, timezone, timedelta

import disnake
from disnake.ext import commands
from loguru import logger

from .ui import ResultsEmbed, GiveawayView
from .models import Giveaway
from .core.enums import GiveawayStatus


class GiveawayManager:
    def __init__(
        self,
        bot: commands.Bot,
    ) -> None:
        self.bot = bot

    async def get_giveaway(
        self,
        message_id: int
    ) -> Giveaway:
        giveaways = await Giveaway.find(
            Giveaway.discord_message_id == message_id
        )
        if not giveaways:
            raise ValueError("Giveaway not found")

        return giveaways[0]

    async def create_giveaway(
        self,
        message_id: int,
        channel_id: int,
        amount: int,
        duration_hours: int,
    ) -> None:
        ends_at = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
        await Giveaway.add(
            discord_message_id=message_id,
            discord_channel_id=channel_id,
            amount=amount,
            ends_at=ends_at
        )
        logger.info("created giveaway with message ID: {}", message_id)

    async def process_result(
        self,
        giveaway: Giveaway
    ) -> None:
        channel = await self.bot.fetch_channel(giveaway.discord_channel_id)
        message = await channel.fetch_message(giveaway.discord_message_id)

        members = await Giveaway.get_random_members(giveaway.discord_message_id, giveaway.amount)
        if not members:
            await Giveaway.set_status(giveaway.id, GiveawayStatus.ENDED)
            await self.disable_buttons(message)
            return

        await Giveaway.set_status(giveaway.id, status=GiveawayStatus.ENDED)
        for idx, member in enumerate(members):
            members[idx] = await self.bot.fetch_user(member.discord_user_id)
        embed = ResultsEmbed(members)

        await message.reply(
            embed=embed
        )
        await self.disable_buttons(message)
        logger.info("processed giveaway results for message ID: {}", giveaway.discord_message_id)

    async def disable_buttons(self, message: disnake.Message) -> None:
        view = GiveawayView(self, is_over=True)
        await message.edit(view=view)
