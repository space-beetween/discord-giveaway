from datetime import datetime, timezone


from disnake.ext import commands, tasks

from ..giveaway_manager import GiveawayManager
from ..core.enums import GiveawayStatus
from ..models import Giveaway


class ResultsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = GiveawayManager(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_giveaways.is_running():
            self.check_giveaways.start()

    @tasks.loop(minutes=1.0)
    async def check_giveaways(self):
        now = datetime.now(timezone.utc)
        ended_giveaways = await Giveaway.find(
            (Giveaway.ends_at <= now) & (Giveaway.status == GiveawayStatus.ACTIVE)
        )
        for giveaway in ended_giveaways:
            await self.manager.process_result(giveaway)

    def cog_unload(self):
        self.check_giveaways.cancel()


def setup(bot: commands.Bot):
    bot.add_cog(ResultsCog(bot))
