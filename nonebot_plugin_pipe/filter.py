from nonebot.adapters.onebot.v12 import Bot, Message, MessageEvent, MessageSegment

from .config import Conv
from .database import get_message


async def default_filter(conv: Conv, bot: Bot, event: MessageEvent) -> Message:
    user_info = await bot.get_user_info(user_id=event.user_id)
    message_out = Message(
        f'{user_info["user_displayname"] or user_info["user_name"]}：'
    )
    for segment in event.message:
        if segment.type == "text":
            message_out += segment
        if segment.type == "image":
            message_out += segment
    if event.reply and (
        message := await get_message(str(conv), event.reply.message_id)
    ):
        message_out = (
            MessageSegment.reply(message.src_id, user_id=message.user_id) + message_out
        )
    return message_out
