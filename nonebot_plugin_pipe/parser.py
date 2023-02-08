from argparse import Namespace as BaseNamespace

from nonebot.rule import ArgumentParser

from .config import Conv


class Namespace(BaseNamespace):
    pipe: str
    conv: Conv
    input: bool
    output: bool
    message: str
    handle: str


parser = ArgumentParser("pipe")
subparsers = parser.add_subparsers(dest="handle")

new = subparsers.add_parser("new", help="创建新的管道", add_help=False)
new.add_argument("pipe", help="管道名称")

delete = subparsers.add_parser("delete", help="删除指定管道", add_help=False)
delete.add_argument("pipe", help="管道名称")

link = subparsers.add_parser("link", help="将本会话连接到指定管道", add_help=False)
link.add_argument("pipe")
link.add_argument("--input", "-I", action="store_true")
link.add_argument("--output", "-O", action="store_true")

unlink = subparsers.add_parser("unlink", help="将本会话连接到指定管道", add_help=False)
unlink.add_argument("pipe")
unlink.add_argument("--input", "-I", action="store_true")
unlink.add_argument("--output", "-O", action="store_true")

filter = subparsers.add_parser("filter", help="设置管道过滤器", add_help=False)
filter.add_argument("pipe")
filter = subparsers.add_parser("filter", help="设置管道过滤器", add_help=False)
filter.add_argument("pipe")
