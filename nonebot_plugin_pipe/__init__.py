from typing import cast

from nonebot.params import ShellCommandArgs
from nonebot import get_bot, get_driver, on_message, on_shell_command
from nonebot.adapters.onebot.v12 import Bot, MessageEvent, OneBotV12AdapterException

from .handle import Handle
from .config import Conv, _config
from .parser import Namespace, parser

command = on_shell_command("pipe", parser=parser, priority=1)
message = on_message(priority=10, block=False)


@command.handle()
async def _(bot: Bot, event: MessageEvent, args: Namespace = ShellCommandArgs()):
    if hasattr(args, "handle"):
        args = getattr(Handle, args.handle)(args)
        await bot.send(event, args.message)
    else:
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
        for conv in pipe.output:
            try:
                bot = cast(Bot, get_bot(conv.bot_id))
                await bot.send_message(
                    detail_type=conv.type,
                    message=event.message,
                    **conv.dict(
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
