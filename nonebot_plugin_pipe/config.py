from pathlib import Path
from json import dumps, loads
from typing import List, Optional

from anyio import open_file
from pydantic.json import pydantic_encoder
from nonebot_plugin_datastore import get_plugin_data
from pydantic import BaseModel, parse_obj_as, root_validator


class Conv(BaseModel):
    type: str
    bot_id: str
    user_id: Optional[str]
    group_id: Optional[str]
    channel_id: Optional[str]
    guild_id: Optional[str]

    def __str__(self) -> str:
        if self.type == "channel":
            return f"{self.bot_id}_{self.type}_{self.guild_id}_{self.channel_id}"
        else:
            return f"{self.bot_id}_{self.type}_{self.group_id or self.user_id}"

    @root_validator
    def _(cls, values):
        if values.get("type") == "channel":
            values["user_id"] = None
            values["group_id"] = None
        elif values.get("type") == "group":
            values["user_id"] = None
        elif values.get("type") == "private":
            values["group_id"] = None
        return values


CONFIG_PATH = get_plugin_data().config_dir


class Pipe(BaseModel):
    name: str
    input: List[Conv]
    output: List[Conv]
    filter: str  # TODO

    def link_conv(self, conv: Conv, input: bool = False, output: bool = False) -> bool:
        if input == output:
            self.input.append(conv)
            self.output.append(conv)
            return True
        if input:
            self.input.append(conv)
        if output:
            self.output.append(conv)
        return True

    def unlink_conv(self, conv: Conv) -> bool:
        for c in self.input:
            if c == conv:
                self.input.remove(c)
        for c in self.output:
            if c == conv:
                self.output.remove(c)
        return True


class Config:
    _path: Path
    _pipes: List[Pipe]

    def __init__(self):
        self._path = CONFIG_PATH / "pipe.json"
        self._pipes = []

    def get_pipe(self, conv: Conv) -> List[Pipe]:
        return [pipe for pipe in self._pipes if conv in pipe.input]

    def add_pipe(self, name: str) -> bool:
        if name in (pipe.name for pipe in self._pipes):
            return False
        self._pipes.append(Pipe(name=name, input=[], output=[], filter=""))
        return True

    def remove_pipe(self, name: str) -> bool:
        for pipe in self._pipes:
            if pipe.name == name:
                self._pipes.remove(pipe)
                return True
        return False

    def link_conv(
        self, name: str, conv: Conv, input: bool = False, output: bool = False
    ) -> bool:
        for pipe in self._pipes:
            if pipe.name == name:
                return pipe.link_conv(conv, input, output)
        return False

    def unlink_conv(self, name: str, conv: Conv) -> bool:
        for pipe in self._pipes:
            if pipe.name == name:
                return pipe.unlink_conv(conv)
        return False

    async def _load(self):
        try:
            async with await open_file(self._path, "r") as f:
                self._pipes = parse_obj_as(List[Pipe], loads(await f.read()))
        except FileNotFoundError:
            pass

    async def _dump(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        async with await open_file(self._path, "w") as f:
            await f.write(
                dumps(
                    self._pipes,
                    indent=4,
                    default=(
                        lambda o: (
                            o.dict(exclude_none=True)
                            if isinstance(o, BaseModel)
                            else pydantic_encoder(o)
                        )
                    ),
                )
            )


_config = Config()
