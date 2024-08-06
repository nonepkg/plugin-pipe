from typing import Optional
from uuid import UUID, uuid4
from collections.abc import Sequence

from sqlalchemy import Uuid, select
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_orm import Model, get_session
from nonebot_plugin_user.models import Bind, User


class Message(Model):
    id: Mapped[Optional[int]] = mapped_column(primary_key=True, default=None)
    message_id: Mapped[UUID] = mapped_column(Uuid, default=uuid4)
    src: Mapped[str]
    src_id: Mapped[str]
    user_id: Mapped[str]


async def get_message(src: str, src_id: str) -> Optional[Message]:
    async with get_session() as session:
        message = (
            await session.scalars(
                select(Message).where(
                    Message.src == src,
                    Message.message_id
                    == select(Message.message_id)
                    .where(Message.src_id == src_id)
                    .scalar_subquery(),
                )
            )
        ).one_or_none()
        if message:
            return message


async def add_message(
    src: str,
    src_id: str,
    user_id: Optional[str] = None,
    message_id: Optional[str] = None,
) -> str:
    async with get_session() as session:
        message = (
            await session.scalars(
                select(Message).where(Message.src_id == src_id, Message.src == src)
            )
        ).one_or_none()
        if message:
            return message.message_id.hex
        message = Message(src=src, src_id=src_id, user_id=user_id)
        if message_id:
            message.message_id = UUID(message_id)
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message.message_id.hex


async def get_user_binds_by_name_or_platform_id(name: str) -> Sequence[Bind]:
    async with get_session() as db_session:
        binds = (
            await db_session.scalars(
                select(Bind)
                .where(User.name == name)
                .join(User, User.id == Bind.bind_id)
            )
        ).all()
    if not binds and "-" in name:
        platform, platform_id = name.split("-", 1)
        binds = (
            await db_session.scalars(
                select(Bind)
                .where(Bind.platform_id == platform_id)
                .where(Bind.platform == platform)
            )
        ).all()
    return binds


async def get_user_binds(platform: str, platform_id: int) -> Sequence[Bind]:
    async with get_session() as db_session:
        binds = (
            await db_session.scalars(
                select(Bind).where(
                    Bind.bind_id
                    == select(User.id)
                    .where(Bind.platform == platform)
                    .where(Bind.platform_id == platform_id)
                    .join(Bind, User.id == Bind.bind_id)
                    .scalar_subquery()
                )
            )
        ).all()
    return binds
