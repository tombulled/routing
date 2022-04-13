from typing import Callable
import mediate


class Middleware(mediate.Middleware[Callable]):
    def append(self, item: Callable, /) -> None:
        ...
