import label
import typing

from . import sentinels
from . import models

def _label(key, hook):
    def decorator(*args, **kwargs):
        values = [hook(arg, **kwargs) for arg in args]

        def wrapper(obj: typing.T, /) -> typing.T:
            labels = label.get(obj)

            labels.setdefault(key, [])

            labels[key] += values

            return obj

        return wrapper

    return decorator

route = _label(sentinels.Route, models.Route)
mount = _label(sentinels.Mount, models.Mount)
middleware = label.marker(sentinels.Middleware)