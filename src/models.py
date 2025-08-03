from typing import Self, List
from datetime import datetime, timezone
from collections.abc import AsyncGenerator

import sqlalchemy as sqla
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncAttrs
)
from sqlalchemy.orm import (
    mapped_column,
    DeclarativeBase,
    Mapped
)
from loguru import logger

from .config import Config
from .core.enums import GiveawayStatus


_conf = Config()


engine = create_async_engine(_conf.db_uri)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    @classmethod
    async def add(
        cls,
        **kw,
    ) -> Self:
        async for session in get_async_session():
            async with session.begin():
                record = cls(**kw)
                session.add(record)
                return record

    @classmethod
    async def find(
        cls,
        *whereclause,
    ) -> List[Self]:
        async for session in get_async_session():
            async with session.begin():
                statement = sqla.select(cls)
                if len(whereclause) != 0:
                    statement = statement.where(*whereclause)

                result = await session.execute(statement)
                return [model for (model, ) in result.all()]


class Giveaway(Base):
    __tablename__ = "giveaways"

    id: Mapped[int] = mapped_column(primary_key=True)
    discord_message_id: Mapped[int] = mapped_column(sqla.BigInteger, unique=True)
    discord_channel_id: Mapped[int] = mapped_column(sqla.BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        sqla.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    amount: Mapped[int] = mapped_column(sqla.Integer)
    ends_at: Mapped[datetime] = mapped_column(sqla.DateTime(timezone=True))
    status: Mapped[GiveawayStatus] = mapped_column(
        sqla.Enum(GiveawayStatus, name="giveaway_stats"),
        default=GiveawayStatus.ACTIVE
    )

    @staticmethod
    async def get_random_members(discord_message_id: int, amount: int) -> List["Member"]:
        async for session in get_async_session():
            async with session.begin():
                stmt = (
                    sqla.select(Member)
                    .where(Member.giveaway_message_id == discord_message_id)
                    .order_by(sqla.func.random())
                    .limit(amount)
                )
                result = await session.execute(stmt)
                return [member for (member,) in result.all()]

    @staticmethod
    async def count_members(discord_message_id: int) -> int:
        async for session in get_async_session():
            async with session.begin():
                stmt = (
                    sqla.select(sqla.func.count())
                    .select_from(Member)
                    .where(Member.giveaway_message_id == discord_message_id)
                )
                result = await session.execute(stmt)
                return result.scalar_one()

    @staticmethod
    async def set_status(giveaway_id: int, status: GiveawayStatus):
        async for session in get_async_session():
            async with session.begin():
                stmt = (
                    sqla.update(Giveaway)
                    .where(Giveaway.id == giveaway_id)
                    .values(status=status)
                )
                await session.execute(stmt)


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    discord_user_id: Mapped[int] = mapped_column(sqla.BigInteger)
    giveaway_message_id: Mapped[int] = mapped_column(
        sqla.BigInteger,
        sqla.ForeignKey("giveaways.discord_message_id")
    )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def setup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database setup completed")
