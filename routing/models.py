import dataclasses
from typing import Any, Callable, Optional

import arguments
import parse


@dataclasses.dataclass
class Mount:
    path: str
    suffix: bool = False

    def apply(self, path: str, *, sep: str = "") -> str:
        return sep.join((path, self.path) if self.suffix else (self.path, path))


@dataclasses.dataclass
class Request:
    path: str
    args: arguments.Arguments


@dataclasses.dataclass(eq=True)
class Route:
    path: str
    target: Optional[Callable[..., Any]] = None

    def match(self, path: str) -> Optional[arguments.Arguments]:
        result: Optional[parse.Result] = parse.parse(self.path, path)

        if result:
            return arguments.Arguments(*result.fixed, **result.named)

        return None

    def matches(self, path: str) -> bool:
        return self.match(path) is not None
