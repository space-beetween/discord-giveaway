from typing import TYPE_CHECKING

import disnake
from loguru import logger

from ...models import Giveaway, Member
from ...core.enums import GiveawayStatus

if TYPE_CHECKING:
    from ...giveaway_manager import GiveawayManager


class JoinButton(disnake.ui.Button):
    def __init__(
        self,
        manager,
        members_count: int = None,
        is_over: bool = False
    ) -> None:
        if members_count is None:
            label = "Join Giveaway"
        else:
            label = f"Join Giveaway ({members_count})"

        self.manager = manager

        super().__init__(
            style=disnake.ButtonStyle.green,
            label=label,
            emoji="🎉",
            custom_id="giveaway",
            disabled=is_over
        )

    async def callback(
        self,
        inter: disnake.MessageInteraction
    ) -> None:
        giveaways = await Giveaway.find(
            Giveaway.discord_message_id == inter.message.id
        )
        if not giveaways:
            await inter.response.send_message("Something went wrong", ephemeral=True)
            return

        giveaway = giveaways[0]
        if giveaway.status == GiveawayStatus.ENDED:
            await inter.response.send_message("Giveaway is over", ephemeral=True)
            return

        members = await Member.find(
            Member.discord_user_id == inter.user.id,
            Member.giveaway_message_id == inter.message.id
        )
        if members:
            await inter.response.send_message(
                "You're already participating in the giveaway.",
                ephemeral=True
            )
            return

        await Member.add(
            discord_user_id=inter.user.id,
            giveaway_message_id=inter.message.id
        )
        logger.info(f'{inter.user.name} joined giveaway with message ID: {inter.message.id}')
        await inter.response.send_message("You've joined the giveaway", ephemeral=True)
        members_count = await Giveaway.count_members(inter.message.id)
        view = GiveawayView(self.manager, members_count)
        await inter.message.edit(view=view)


class EndButton(disnake.ui.Button):
    def __init__(
        self,
        manager: "GiveawayManager",
        is_over: bool = False
    ) -> None:
        self.manager = manager

        super().__init__(
            style=disnake.ButtonStyle.gray,
            label="End Giveaway",
            emoji="❌",
            custom_id="end",
            disabled=is_over
        )

    async def callback(
        self,
        inter: disnake.MessageInteraction
    ) -> None:
        if not inter.author.guild_permissions.administrator:
            await inter.response.send_message(
                "You don't have permission to end the giveaway",
                ephemeral=True
            )
            return

        giveaway = await self.manager.get_giveaway(inter.message.id)
        if giveaway.status == GiveawayStatus.ENDED:
            await inter.response.send_message(
                "Giveaway is over",
                ephemeral=True
            )
            return

        await inter.response.send_message(
            "Giveaway is ending",
            ephemeral=True
        )
        await self.manager.process_result(giveaway)


class GiveawayView(disnake.ui.View):
    def __init__(
        self,
        manager: "GiveawayManager",
        members_count: int = None,
        is_over: bool = False
    ):
        super().__init__(timeout=None)
        self.add_item(JoinButton(manager, members_count, is_over))
        self.add_item(EndButton(manager, is_over))
