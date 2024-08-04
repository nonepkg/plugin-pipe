from typing import cast
from argparse import Namespace

from nonebot.permission import SUPERUSER
from nonebot.params import ShellCommandArgs
from nonebot.plugin import PluginMetadata, require
from nonebot import get_bot, get_driver, on_message, on_shell_command
from nonebot.adapters.onebot.v12 import Bot, MessageEvent, OneBotV12AdapterException

require("nonebot_plugin_localstore")
require("nonebot_plugin_orm")

from .handle import Handle
from .parser import parser
from .config import Conv, _config
from .database import add_message
from .filter import default_filter

__plugin_meta__ = PluginMetadata(
    name="会话转接",
    description="在 OneBot V12 会话间转发消息",
    usage="""看 README""",
    type="application",
    homepage="https://github.com/nonepkg/plugin-pipe",
    supported_adapters={"~onebot.v12"},
)


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
                message = await default_filter(c, bot, event)
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
