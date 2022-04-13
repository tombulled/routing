import inspect

"""
Aim: Get reference to `Foo` in `dec`
"""


def dec(f):
    print(f)

    frame = inspect.currentframe()

    try:
        f_locals = frame.f_back.f_locals

        print(frame.f_back)
        print(frame.f_back.f_locals)
        print(frame.f_back.f_globals)

        module = f_locals.get("__name__") or f_locals.get("__module__")
        qualname = f_locals.get("__qualname__")
        if qualname is not None:
            module += f".{qualname}"

        print(module)
    finally:
        del frame

    return f


class Foo:
    @dec(Foo)
    def bar(self):
        print("bar")


f = Foo()

f.bar()
