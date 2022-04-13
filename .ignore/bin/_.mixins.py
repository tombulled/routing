from typing import Optional, Callable


class InverseRouterMixin(object):
    def build(self, *args, **kwargs):
        return super().build(*args, **kwargs).copy(params=addict.Dict())

    def route(self, *args, **kwargs):
        super_route = super().route

        def decorator(target: Optional[Callable] = None):
            if target is None:

                def decorator(request):
                    def wrapper(**params):
                        return request.copy(params=params)

                    return wrapper

                target = decorator

            return super_route(*args, **kwargs)(target)

        return decorator
