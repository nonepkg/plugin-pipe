from typing import cast
from argparse import Namespace

from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata, require
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot import get_bot, get_driver, on_command, on_message, on_shell_command
from nonebot.adapters.onebot.v12 import (
    Bot,
    Message,
    MessageEvent,
    MessageSegment,
    OneBotV12AdapterException,
)

require("nonebot_plugin_localstore")
require("nonebot_plugin_orm")
require("nonebot_plugin_user")

from nonebot_plugin_user import User
from nonebot_plugin_user.utils import set_user_name

from .handle import Handle
from .parser import parser
from .config import Conv, _config
from .filter_ import default_filter
from .database import add_message, get_user_binds_by_name_or_platform_id

__plugin_meta__ = PluginMetadata(
    name="会话转接",
    description="在 OneBot V12 会话间转发消息",
    usage="""看 README""",
    type="application",
    homepage="https://github.com/nonepkg/plugin-pipe",
    supported_adapters={"~onebot.v12"},
)


pipe = on_shell_command("pipe", parser=parser, permission=SUPERUSER, priority=1)
at = on_command("at", priority=1, block=True)
message = on_message(priority=10, block=False)


@pipe.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    args.conv = Conv(
        type=event.detail_type,
        bot_id=bot.self_id,
        **event.dict(include={"user_id", "group_id", "channel_id", "guild_id"}),
    )
    if hasattr(args, "handle"):
        await getattr(Handle, args.handle)(args)
    await bot.send(event, args.message)


@at.handle()
async def _(bot: Bot, event: MessageEvent, user: User, arg: Message = CommandArg()):
    conv = Conv(
        type=event.detail_type,
        bot_id=bot.self_id,
        **event.dict(include={"user_id", "group_id", "channel_id", "guild_id"}),
    )
    message_id = await add_message(str(conv), event.message_id, event.user_id)
    pipes = _config.get_pipe(conv)
    binds = await get_user_binds_by_name_or_platform_id(arg.extract_plain_text())
    if not binds:
        await bot.send(event, "该用户不存在！")
        return
    for pipe in pipes:
        for c in pipe.output:
            if c == conv:
                continue
            try:
                bot_out = cast(Bot, get_bot(c.bot_id))
                if user.name != f"{bot.platform}-{event.user_id}":
                    user_name = user.name
                else:
                    user_info = await bot.get_user_info(user_id=event.user_id)
                    user_name = user_info["user_displayname"] or user_info["user_name"]
                    await set_user_name(bot.platform, event.user_id, user_name)
                message_out = Message(f"{user_name}：")
                for bind in binds:
                    if bind.platform != bot_out.platform:
                        continue
                    message_out += MessageSegment.mention(bind.platform_id)
                await add_message(
                    str(c),
                    (
                        await bot_out.send_message(
                            detail_type=c.type,
                            message=message_out,
                            **c.dict(
                                include={
                                    "user_id",
                                    "group_id",
                                    "channel_id",
                                    "guild_id",
                                },
                                exclude_none=True,
                            ),
                        )
                    )["message_id"],
                    bot_out.self_id,
                    message_id,
                )
            except KeyError:
                pass
            except OneBotV12AdapterException:
                pass


@message.handle()
async def _(bot: Bot, event: MessageEvent, user: User):
    conv = Conv(
        type=event.detail_type,
        bot_id=bot.self_id,
        **event.dict(include={"user_id", "group_id", "channel_id", "guild_id"}),
    )
    message_id = await add_message(str(conv), event.message_id, event.user_id)
    pipes = _config.get_pipe(conv)
    for pipe in pipes:
        for c in pipe.output:
            if c == conv:
                continue
            try:
                bot_out = cast(Bot, get_bot(c.bot_id))
                message = await default_filter(c, bot, bot_out, event, user)
                await add_message(
                    str(c),
                    (
                        await bot_out.send_message(
                            detail_type=c.type,
                            message=message,
                            **c.dict(
                                include={
                                    "user_id",
                                    "group_id",
                                    "channel_id",
                                    "guild_id",
                                },
                                exclude_none=True,
                            ),
                        )
                    )["message_id"],
                    bot_out.self_id,
                    message_id,
                )
            except KeyError:
                pass
            except OneBotV12AdapterException:
                pass


driver = get_driver()


@driver.on_startup
async def _():
    await _config._load()
