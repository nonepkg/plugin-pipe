from pathlib import Path
from json import dumps, loads
from typing import List, Optional

from anyio import open_file
from pydantic.json import pydantic_encoder
from pydantic import BaseModel, parse_obj_as, root_validator


class Conv(BaseModel):
    type: str
    user_id: Optional[str]
    group_id: Optional[str]
    channel_id: Optional[str]
    guild_id: Optional[str]

    @root_validator
    def _(cls, values):
        if values.get("type") == "group":
            values["user_id"] = None
        elif values.get("type") == "private":
            values["group_id"] = None
        return values


class Pipe(BaseModel):
    name: str
    input: List[Conv]
    output: List[Conv]
    filter: str  # TODO


class Config:
    _path: Path
    _pipes: List[Pipe]

    def __init__(self, path: Path = Path() / "data" / "pipe" / "config.json"):
        self._path = path
        self._pipes = []

    def get_pipe(self, conv: Conv) -> List[Pipe]:
        return [pipe for pipe in self._pipes if conv in pipe.input]

    async def _load(self):
        try:
            async with await open_file(self._path, "r") as f:
                self._pipes = parse_obj_as(List[Pipe], loads(await f.read()))
        except FileNotFoundError:
            pass

    async def _dump(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        async with await open_file(self._path, "w") as f:
            await f.write(dumps(self._pipes, indent=4, default=pydantic_encoder))


_config = Config()
