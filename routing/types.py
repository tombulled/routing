import parse

from typing import Optional

class Path(str):
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({super().__repr__()})'

    def __invert__(self):
        return self.reduce()

    def reduce(self) -> str:
        return self.format(** dict.fromkeys(parse.compile(self).named_fields, str(dict())))

    def parse(self, path: str, **kwargs) -> Optional[dict]:
        return (result := parse.parse(self, path, **kwargs)) and result.named

    def matches(self, path: str, **kwargs) -> bool:
        return self.parse(path, **kwargs) is not None

    def reductively_equals(self, path: 'Path', case_sensitive: bool = True):
        operands = map(self.__class__.reduce, (self, path))

        if not case_sensitive:
            operands = map(self.__class__.lower, operands)

        return operator.eq(*operands)

# class AnyPath(Path):
#     def __init__(self):
#         super().__init__('*')
#
#     def __repr__(self) -> str:
#         return 'Path(*)'
#
#     def __eq__(self, rhs: str) -> bool:
#         return True
