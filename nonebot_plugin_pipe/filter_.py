from pathlib import Path
from collections.abc import Sequence

from nonebot_plugin_user.models import Bind
from nonebot_plugin_htmlrender import template_to_pic
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
        if segment.type == "message_nodes":
            for node in segment.data["nodes"]:
                node["image"] = []
                node["text"] = ""
                for seg in node["message"]:
                    if seg["type"] == "image":
                        node["image"].append(
                            (
                                await bot.get_file(
                                    type="url", file_id=seg["data"]["file_id"]
                                )
                            )["url"]
                        )
                    else:
                        node["text"] += str(seg["data"].get("text", ""))
                del node["message"]
            file_id = (
                await bot_out.upload_file(
                    type="data",
                    name="nodes.",
                    data=await template_to_pic(
                        str(Path(__file__).parent / "templates"),
                        "nodes.html",
                        {"message_nodes": segment.data["nodes"]},
                        {
                            "viewport": {"width": 800, "height": 10},
                        },
                    ),
                )
            )["file_id"]
            message_out += MessageSegment.image(file_id=file_id)

    if event.reply and (
        message := await get_message(str(conv), event.reply.message_id)
    ):
        message_out = (
            MessageSegment.reply(message.src_id, user_id=message.user_id) + message_out
        )
    return message_out
