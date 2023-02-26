from uuid import UUID, uuid4
from typing import Optional

from sqlmodel import Field, select
from nonebot_plugin_datastore import create_session, get_plugin_data

plugin_data = get_plugin_data()
Model = plugin_data.Model


class Message(Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: UUID = Field(default_factory=uuid4)
    src: str
    src_id: str
    user_id: Optional[str] = None


async def get_message(src: str, src_id: str) -> Optional[Message]:
    async with create_session() as session:
        message = (
            await session.execute(
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
            return message[0]


async def add_message(
    src: str,
    src_id: str,
    user_id: Optional[str] = None,
    message_id: Optional[str] = None,
) -> str:
    async with create_session() as session, session.begin():
        message = (
            await session.execute(
                select(Message).where(Message.src_id == src_id, Message.src == src)
            )
        ).one_or_none()
        if message:
            return message[0].message_id.hex
        message = Message(src=src, src_id=src_id, user_id=user_id)
        if message_id:
            message.message_id = UUID(message_id)
        session.add(message)
        return message.message_id.hex
