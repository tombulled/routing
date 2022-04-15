from typing import Any

import annotate

from . import models, sentinels


@annotate.annotation(key=sentinels.Route, repeatable=True)
def route(*args: Any, **kwargs: Any) -> models.Route:
    return models.Route(*args, **kwargs)


@annotate.marker(key=sentinels.Middleware)
def middleware() -> None:
    return None
