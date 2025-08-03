from datetime import datetime, timezone, timedelta

import disnake


class GiveawayEmbed(disnake.Embed):
    def __init__(
        self,
        prize: str,
        duration_hours: int
    ) -> None:
        timestamp = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
        super().__init__(
            title=f"🎁 {prize}",
            color=disnake.Color.blue(),
            timestamp=timestamp
        )

        self.set_footer(text="Results at:")
