from typing import cast
from argparse import Namespace

from nonebot.permission import SUPERUSER
from nonebot.params import ShellCommandArgs
from nonebot import get_bot, get_driver, on_message, on_shell_command
from nonebot.adapters.onebot.v12 import Bot, MessageEvent, OneBotV12AdapterException

from .handle import Handle
from .parser import parser
from .config import Conv, _config
from .filter import default_filter
from .database import add_message

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
        await getattr(Handle, args.handle)(args)
    await bot.send(event, args.message)


@message.handle()
async def _(bot: Bot, event: MessageEvent):
    message_id = await add_message(bot.platform, event.message_id, event.user_id)
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
                bot_out = cast(Bot, get_bot(c.bot_id))
                message = await default_filter(bot, event, bot_out)
                await add_message(
                    bot_out.platform,
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
