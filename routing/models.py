import dataclasses
import typing

@dataclasses.dataclass
class Context:
    args:   tuple = dataclasses.field(default_factory = tuple)
    kwargs: dict  = dataclasses.field(default_factory = dict)

@dataclasses.dataclass
class Mount:
    path: typing.Any

@dataclasses.dataclass
class Request:
    path:   str
    # router: 'Router'
    params: Context
    # context: Context

@dataclasses.dataclass
class Route:
    path: str
    target: typing.Any = None