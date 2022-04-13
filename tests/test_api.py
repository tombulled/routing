import routing
from routing import api


def test_get_middleware() -> None:
    @routing.middleware
    def function(*args, **kwargs) -> None:
        ...

    @routing.middleware
    class CallableClass:
        def __call__(self, *args, **kwargs) -> None:
            ...

    class Class:
        @routing.middleware
        def method(self, *args, **kwargs) -> None:
            ...

    callable_cls = CallableClass()
    cls = Class()

    assert api.get_middleware(function) == [function]
    assert api.get_middleware(CallableClass) == [CallableClass]
    assert api.get_middleware(callable_cls) == [callable_cls]
    assert api.get_middleware(Class) == [Class.method]
    assert api.get_middleware(cls) == [cls.method]
