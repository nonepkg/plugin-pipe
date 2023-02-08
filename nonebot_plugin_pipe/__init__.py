from typing import cast
from argparse import Namespace

from nonebot.permission import SUPERUSER
from nonebot.params import ShellCommandArgs
from nonebot import get_bot, get_driver, on_message, on_shell_command
from nonebot.adapters.onebot.v12 import Bot, MessageEvent, OneBotV12AdapterException

from .handle import Handle
from .parser import parser
from .config import Conv, _config

command = on_shell_command("pipe", parser=parser, permission=SUPERUSER, priority=1)
message = on_message(priority=10, block=False)


@command.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    args.conv = Conv(
        type=event.detail_type,
        bot_id=bot.self_id,
        **event.dict(include={"user_id", "group_id", "channel_id", "guild_id"}),
    )
    if hasattr(args, "handle"):
        getattr(Handle, args.handle)(args)
    await bot.send(event, args.message)


@message.handle()
async def _(bot: Bot, event: MessageEvent):
    conv = Conv(
        type=event.detail_type,
        bot_id=bot.self_id,
        **event.dict(include={"user_id", "group_id", "channel_id", "guild_id"}),
    )
    pipes = _config.get_pipe(conv)
    for pipe in pipes:
        for c in pipe.output:
            if c == conv:
                continue
            try:
                bot = cast(Bot, get_bot(c.bot_id))
                await bot.send_message(
                    detail_type=c.type,
                    message=event.message,
                    **c.dict(
                        include={"user_id", "group_id", "channel_id", "guild_id"},
                        exclude_none=True,
                    ),
                )
            except KeyError:
                pass
            except OneBotV12AdapterException:
                pass


driver = get_driver()


@driver.on_startup
async def _():
    await _config._load()


@driver.on_shutdown
async def _():
    await _config._dump()
