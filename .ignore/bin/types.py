import collections
import dataclasses
import typing

import parse

# This is a bit like pathlib.Path
@dataclasses.dataclass
class Path:
    path: str

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.path!r})"

    def __truediv__(self, rhs) -> "Path":
        print("div:", self, rhs)

    # parent, parents, join, match, parts

    # def __invert__(self):
    #     return self.reduce()
    #
    # Implement this as __hash__ ?
    # def reduce(self) -> str:
    #     return self.data.format(** dict.fromkeys(parse.compile(self.data).named_fields, str(dict())))
    #
    # def parse(self, path: str, **kwargs) -> typing.Optional[dict]:
    #     return (result := parse.parse(self.data, path, **kwargs)) and result.named
    #
    # def matches(self, path: str, **kwargs) -> bool:
    #     return self.parse(path, **kwargs) is not None
    #
    # def reductively_equals(self, path: 'Path', case_sensitive: bool = True):
    #     operands = map(self.__class__.reduce, (self, path))
    #
    #     if not case_sensitive:
    #         operands = map(self.__class__.lower, operands)
    #
    #     return operator.eq(*operands)
