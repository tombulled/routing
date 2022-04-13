import dataclasses
from typing import Any, Callable, Optional, TypeVar
import parse
import arguments

@dataclasses.dataclass
class Mount:
    path: str
    # sep: str = ''
    suffix: bool = False

    # def apply(self, path: str, /) -> str:
    #     """
    #     Apply the mount to a given path
    #     """

    #     return self.sep.join((path, self.path) if self.suffix else (self.path, path))


@dataclasses.dataclass
class Request:
    path: str
    args: arguments.Arguments


@dataclasses.dataclass(eq=True)
class Route:
    path: str
    target: Callable[..., Any] = lambda *args, **kwargs: None

    def match(self, path: str) -> Optional[arguments.Arguments]:
        result: Optional[parse.Result] = parse.parse(self.path, path)

        if result:
            return arguments.Arguments(*result.fixed, **result.named)

    def matches(self, path: str) -> bool:
        return self.match(path) is not None