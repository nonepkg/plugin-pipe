from typing import Annotated

from nonebot.params import Depends
from nonebot_plugin_user import User
from nonebot_plugin_user.utils import set_user_name
from nonebot.adapters.onebot.v12 import Bot, MessageEvent

from .config import Conv as _Conv


async def _user_name(bot: Bot, event: MessageEvent, user: User) -> str:
    if user.name != f"{bot.platform}-{event.user_id}":
        user_name = user.name
    else:
        user_info = await bot.get_user_info(user_id=event.user_id)
        user_name = user_info["user_displayname"] or user_info["user_name"]
        await set_user_name(bot.platform, event.user_id, user_name)
    return user_name


def UserName() -> str:
    return Depends(_user_name)


async def _conv(bot: Bot, event: MessageEvent) -> _Conv:
    return _Conv(
        type=event.detail_type,
        bot_id=bot.self_id,
        **event.dict(include={"user_id", "group_id", "channel_id", "guild_id"}),
    )


Conv = Annotated[_Conv, Depends(_conv)]
