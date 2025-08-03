import disnake
from disnake.ext import commands


class ErrorHandler(commands.Cog):
    @commands.Cog.listener()
    async def on_slash_command_error(
        self,
        inter: disnake.AppCmdInter,
        error: Exception
    ) -> None:
        if isinstance(error, commands.CommandError):
            await inter.response.send_message(
                str(error),
                ephemeral=True
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(ErrorHandler())
