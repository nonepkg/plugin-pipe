from collections.abc import Sequence

from nonebot_plugin_user.models import Bind
from nonebot.adapters.onebot.v12 import Bot, Message, MessageEvent, MessageSegment

from .config import Conv
from .database import get_message, get_user_binds


async def at_filter(
    conv: Conv,
    bot: Bot,
    bot_out: Bot,
    event: MessageEvent,
    user_name: str,
    binds: Sequence[Bind],
) -> Message:
    message_out = Message(f"{user_name}：")
    for bind in binds:
        if bind.platform != bot_out.platform:
            continue
        message_out += MessageSegment.mention(bind.platform_id)
    if event.reply and (
        message := await get_message(str(conv), event.reply.message_id)
    ):
        message_out = (
            MessageSegment.reply(message.src_id, user_id=message.user_id) + message_out
        )
    return message_out


async def default_filter(
    conv: Conv,
    bot: Bot,
    bot_out: Bot,
    event: MessageEvent,
    user_name: str,
) -> Message:
    message_out = Message(f"{user_name}：")
    for segment in event.message:
        if segment.type == "text":
            message_out += segment
        if segment.type == "image":
            message_out += segment
        if segment.type == "mention":
            binds = await get_user_binds(bot.platform, segment.data["user_id"])
            for bind in binds:
                if bind.platform != bot_out.platform:
                    continue
                message_out += MessageSegment.mention(bind.platform_id)

    if event.reply and (
        message := await get_message(str(conv), event.reply.message_id)
    ):
        message_out = (
            MessageSegment.reply(message.src_id, user_id=message.user_id) + message_out
        )
    return message_out
