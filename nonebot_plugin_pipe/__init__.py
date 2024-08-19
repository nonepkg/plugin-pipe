from typing import cast
from argparse import Namespace

from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata, require
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot import get_bot, get_driver, on_command, on_message, on_shell_command
from nonebot.adapters.onebot.v12 import (
    Bot,
    Message,
    MessageEvent,
    OneBotV12AdapterException,
)

require("nonebot_plugin_localstore")
require("nonebot_plugin_orm")
require("nonebot_plugin_user")
require("nonebot_plugin_htmlrender")


from .handle import Handle
from .parser import parser
from .config import _config
from .params import Conv, UserName
from .filter_ import at_filter, default_filter
from .database import add_message, get_user_binds_by_name_or_platform_id

__plugin_meta__ = PluginMetadata(
    name="会话转接",
    description="在 OneBot V12 会话间转发消息",
    usage="""看 README""",
    type="application",
    homepage="https://github.com/nonepkg/plugin-pipe",
    supported_adapters={"~onebot.v12"},
)


pipe = on_shell_command(
    "pipe", parser=parser, permission=SUPERUSER, priority=1, block=True
)
at = on_command("at", priority=1, block=True)
message = on_message(priority=10, block=False)


@pipe.handle()
async def _(matcher: Matcher, conv: Conv, args: Namespace = ShellCommandArgs()):
    args.conv = conv
    if hasattr(args, "handle"):
        await getattr(Handle, args.handle)(args)
    await matcher.send(args.message)


async def send_to_pipes(
    bot: Bot,
    event: MessageEvent,
    conv: Conv,
    user_name: str,
    filter_=default_filter,
    **kwargs,
):
    message_id = await add_message(str(conv), event.message_id, event.user_id)
    pipes = _config.get_pipe(conv)
    for pipe in pipes:
        for c in pipe.output:
            if c == conv:
                continue
            try:
                bot_out = cast(Bot, get_bot(c.bot_id))
            except KeyError:
                continue
            message = await filter_(c, bot, bot_out, event, user_name, **kwargs)
            try:
                resp = await bot_out.send_message(
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
            except OneBotV12AdapterException as e:
                logger.opt(exception=e).error(f"Failed to send message to {c}")
                continue
            await add_message(
                str(c),
                resp["message_id"],
                bot_out.self_id,
                message_id,
            )


@at.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    conv: Conv,
    user_name: str = UserName(),
    arg: Message = CommandArg(),
):
    binds = await get_user_binds_by_name_or_platform_id(arg.extract_plain_text())
    if not binds:
        await bot.send(event, "该用户不存在！")
        return
    await send_to_pipes(bot, event, conv, user_name, at_filter, binds=binds)


@message.handle()
async def _(bot: Bot, event: MessageEvent, conv: Conv, user_name: str = UserName()):
    await send_to_pipes(bot, event, conv, user_name)


@get_driver().on_startup
async def _():
    await _config._load()
