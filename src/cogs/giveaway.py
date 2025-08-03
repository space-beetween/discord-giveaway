import disnake
from disnake.ext import commands
from disnake.ext.commands import Param

from ..ui import GiveawayView, GiveawayEmbed
from ..giveaway_manager import GiveawayManager


class GiveawayCog(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
    ):
        self.bot = bot
        self.manager = GiveawayManager(bot)

    @commands.slash_command(
        description="Start a giveaway. Requires administrator permissions.",
    )
    @commands.has_permissions(administrator=True)
    async def start(
        self,
        inter: disnake.AppCmdInter,
        number_of_winners: int = Param(description="Number of winners", ge=1),
        prize: str = Param(description="The prize for the giveaway"),
        duration_hours: int = Param(description="Duration of the giveaway in hours", ge=1)
    ) -> None:
        embed = GiveawayEmbed(
            prize=prize,
            duration_hours=duration_hours
        )
        view = GiveawayView(self.manager)
        await inter.response.send_message(
            embed=embed,
            view=view
        )
        message = await inter.original_response()
        await self.manager.create_giveaway(
            message_id=message.id,
            channel_id=message.channel.id,
            amount=number_of_winners,
            duration_hours=duration_hours
        )


def setup(bot: commands.Bot):
    bot.add_cog(GiveawayCog(bot))
