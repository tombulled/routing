import typing as t


def parametrise(request, call_next: t.Callable) -> t.Any:
    return call_next(**request.params)
