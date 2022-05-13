from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from arguments import Arguments

import parse


@dataclass
class Mount:
    path: str
    suffix: bool = False

    def apply(self, path: str, *, sep: str = "") -> str:
        return sep.join((path, self.path) if self.suffix else (self.path, path))


@dataclass
class AbstractRequest(ABC):
    path: str
    data: Any = None


class Request(AbstractRequest):
    data: Arguments = field(default_factory=Arguments)


@dataclass(eq=True)
class AbstractRoute(ABC):
    path: str
    target: Optional[Callable[..., Any]] = None

    def matches(self, path: str) -> bool:
        return path == self.path


class Route(AbstractRoute):
    def match(self, path: str) -> Optional[Arguments]:
        result: Optional[parse.Result] = parse.parse(self.path, path)

        if result:
            return Arguments(*result.fixed, **result.named)

        return None

    def matches(self, path: str) -> bool:
        return self.match(path) is not None
