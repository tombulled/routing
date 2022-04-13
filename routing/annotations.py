import annotate

from . import models, sentinels


@annotate.annotation(key=sentinels.Route, repeatable=True)
def route(*args, **kwargs) -> models.Route:
    return models.Route(*args, **kwargs)


# @annotate.annotation(key=sentinels.Mount, repeatable=True)
# def mount(*args, **kwargs) -> models.Mount:
#     return models.Mount(*args, **kwargs)


@annotate.marker(key=sentinels.Middleware)
def middleware() -> None:
    return None
