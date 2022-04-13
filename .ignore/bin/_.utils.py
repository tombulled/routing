import typing as t


def handler(func: t.Callable) -> t.Callable:
    def wrapper(request):
        return func(**request.params)

    return wrapper
