from .config import _config
from .parser import Namespace


class Handle:
    @staticmethod
    async def new(args: Namespace):
        if _config.add_pipe(args.pipe):
            await _config._dump()
            args.message = f"新建管道「{args.pipe}」成功"
        else:
            args.message = f"已经存在命名为「{args.pipe}」的管道"

    @staticmethod
    async def delete(args: Namespace):
        if _config.remove_pipe(args.pipe):
            await _config._dump()
            args.message = f"删除管道「{args.pipe}」成功"
        else:
            args.message = f"名为「{args.pipe}」的管道不存在"

    @staticmethod
    async def list(args: Namespace):
        args.message = "所有管道：\n{}".format(
            "\n".join(f"- {pipe.name}" for pipe in _config._pipes)
        )

    @staticmethod
    async def show(args: Namespace):
        for pipe in _config._pipes:
            if pipe.name == args.pipe:
                args.message = "{}\n输入：\n{}\n输出：\n{}".format(
                    f"管道「{args.pipe}」连接状态：",
                    "\n".join(f"- {conv}" for conv in pipe.input),
                    "\n".join(f"- {conv}" for conv in pipe.output),
                )
                return
        args.message = f"名为「{args.pipe}」的管道不存在"

    @staticmethod
    async def link(args: Namespace):
        if _config.link_conv(args.pipe, args.conv, args.input, args.output):
            await _config._dump()
            args.message = f"成功将本会话连接到管道「{args.pipe}」"
        else:
            args.message = f"管道「{args.pipe}」不存在"

    @staticmethod
    async def unlink(args: Namespace):
        if _config.unlink_conv(args.pipe, args.conv):
            await _config._dump()
            args.message = f"成功解除本会话与管道「{args.pipe}」的连接"
        else:
            args.message = f"管道「{args.pipe}」不存在"

    @staticmethod
    async def filter(args: Namespace):
        args.message = "尚未支持"

    @staticmethod
    async def info(args: Namespace):
        args.message = "尚未支持"
