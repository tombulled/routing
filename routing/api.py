import dataclasses
import inspect

import annotate
import mediate

from . import models, routers, sentinels


def get_routes(obj, *, sep: str = ""):
    annotations = annotate.get_annotations(obj)

    if sentinels.Route in annotations:
        return [
            dataclasses.replace(target=obj) for route in annotations[sentinels.Route]
        ]

    return [
        dataclasses.replace(route, target=member)
        for name, member in inspect.getmembers(obj)
        for route in annotate.get_annotations(member).get(sentinels.Route, ())
    ]


def get_middleware(obj):
    if sentinels.Middleware in annotate.get_annotations(obj):
        return [obj]

    return [
        member
        for name, member in inspect.getmembers(obj)
        if sentinels.Middleware in annotate.get_annotations(member)
    ]


def router(*objs, sep: str = ""):
    middlewares = mediate.Middleware()

    for obj in objs:
        for m in get_middleware(obj):
            middlewares.append(m)

    return routers.Router(
        routes=[
            route
            for obj in objs
            for route in (
                [obj] if isinstance(obj, models.Route) else get_routes(obj, sep=sep)
            )
        ],
        middlewares=middlewares,
    )
