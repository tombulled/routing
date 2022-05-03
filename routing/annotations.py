from typing import Any

import annotate

from . import models, enums


@annotate.annotation(key=enums.Annotation.ROUTE, repeatable=True)
def route(*args: Any, **kwargs: Any) -> models.Route:
    return models.Route(*args, **kwargs)


@annotate.marker(key=enums.Annotation.MIDDLEWARE)
def middleware() -> None:
    return None
