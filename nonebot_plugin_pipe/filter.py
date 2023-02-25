from nonebot.adapters.onebot.v12 import Bot, Message, MessageEvent


async def default_filter(bot: Bot, event: MessageEvent) -> Message:
    user_info = await bot.get_user_info(user_id=event.user_id)
    message_out = Message(f'{user_info["user_displayname"] or user_info["user_name"]}：')
    for message in event.message:
        if message.type == "text":
            message_out += message
        if message.type == "image":
            message_out += message
    return message_out
