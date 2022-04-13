import routing
import routing.sentinels
import routing.types

import dataclasses
import inspect
import math

import label
import sentinel

"""
Notes:
    * Offload path segment concatenation to 'concatenate'
        * Defaults:
            int: int()
            dict: dict()
            set: set()
            str: str()
            list: list()
            tuple: tuple()
            bytes: bytes()

    * Implement descriptors?
    * Implement mounts
    * Request.path only makes sense as a string
        - NO! Stay true to the original idea!
            - By all means default to strings however...

Mounts should work with separators other than '/', e.g:
    @mount('go to')
    class Controller:
        @route('tesco')
        def go_to_tesco(...): ...

        @route('jail')
        def go_to_jail(...): ...

Examples of non-string paths: (int, float, list, enum)
    # Example for a list: [Request.HEARTBEAT, RequestType.Request]
    @mount(Request.HEARTBEAT)
    class Controller:
        @route(RequestType.Request)
        def handle_request(...): ...

        @route(RequestType.Response)
        def handle_response(...): ...

    # Example for bytes: 0xAB53
    @mount(0xAB)
    class Controller:
        @route(0x53)
        def handle_53(...): ...

        @route(0x2A)
        def handle_2A(...): ...

    # Example for binary: 0b1101
    @mount(0b11)
    class Controller:
        @route(0b01)
        def handle_1(...): ...

        @route(0b10)
        def handle_2(...): ...
"""

import collections
import pathlib
import furl

_p = "/foo/{bar}"
_p2 = "go {direction}"

"""
How can params be specified for non-string types?
0b10{seg}11 ??
Use a mask? (uses AND)

@mount(0b10)
class Foo:
    @route(0b00, mask=OR, size=2)
    def ...:
        ...

    @route(0b11, mask=AND)
    def ...:
        ...

"""


@mount(0b10)
class Foo:
    @route(
        0b00, mask=OR, size=2
    )  # NOTE: Use a default path of 0b0 (and '/' for string-based?)
    def foo():
        ...


p = routing.types.Path(_p)
p2 = pathlib.Path(_p)
p3 = furl.Path(_p)


@dataclasses.dataclass
class Counter:
    count: int = 0

    @staticmethod
    @routing.middleware
    def log(call_next, request):
        print(f"[Log] Request: {request}")
        response = call_next(request)
        print(f"[Log] Response: {response}")
        return response

    @routing.route("/add/{amount:d}")
    def add(self, amount: int, multiplier: int = 1) -> None:
        self.count += amount * multiplier

    @routing.route("/get")
    def get(self) -> int:
        return self.count


counter = Counter(50)


@routing.mount("/dangerous")
@routing.route("/reset")
def reset():
    counter.count = 0


router = routing.router(counter, reset)


@routing.mount("/a")
@routing.mount("/b", "/c")
@routing.route("/foo")
@routing.route("/bar")
def foo():
    return "foo"


r = routing.Router()


@r.route("/bar")
def bar():
    return "bar"


@r.middleware
def process(call_next, request):
    return call_next(request)


r["a"] = 1

router("/add/5?multiplier=2", method="post")
