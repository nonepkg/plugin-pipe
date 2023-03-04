from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Uuid, select
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_datastore import create_session, get_plugin_data

plugin_data = get_plugin_data()
Model = plugin_data.Model


class Message(Model):
    id: Mapped[Optional[int]] = mapped_column(primary_key=True, default=None)
    message_id: Mapped[UUID] = mapped_column(Uuid, default=uuid4)
    src: Mapped[str]
    src_id: Mapped[str]
    user_id: Mapped[Optional[str]]


async def get_message(src: str, src_id: str) -> Optional[Message]:
    async with create_session() as session:
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
    async with create_session() as session:
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
