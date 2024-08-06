from nonebot_plugin_user import User
from nonebot_plugin_user.utils import set_user_name
from nonebot.adapters.onebot.v12 import Bot, Message, MessageEvent, MessageSegment

from .config import Conv
from .database import get_message, get_user_binds


async def default_filter(
    conv: Conv, bot: Bot, bot_out: Bot, event: MessageEvent, user: User
) -> Message:
    if user.name != f"{bot.platform}-{event.user_id}":
        user_name = user.name
    else:
        user_info = await bot.get_user_info(user_id=event.user_id)
        user_name = user_info["user_displayname"] or user_info["user_name"]
        await set_user_name(bot.platform, event.user_id, user_name)
    message_out = Message(f"{user_name}：")
    for segment in event.message:
        if segment.type == "text":
            message_out += segment
        if segment.type == "image":
            message_out += segment
        if segment.type == "mention" and (
            binds := await get_user_binds(bot.platform, segment.data["user_id"])
        ):
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
