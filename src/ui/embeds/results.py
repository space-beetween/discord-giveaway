from typing import List

import disnake


class ResultsEmbed(disnake.Embed):
    def __init__(
        self,
        winners: List[disnake.Member]
    ) -> None:
        description = ''
        for winner in winners:
            description += f'{winner.mention}\n'
        super().__init__(
            title="🎉 Results",
            color=0x969600,
            description=description
        )
