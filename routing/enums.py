import enum


class Annotation(enum.Enum):
    def __repr__(self) -> str:
        return f"<{type(self).__name__}.{self.name}>"

    ROUTE = enum.auto()
    MIDDLEWARE = enum.auto()
