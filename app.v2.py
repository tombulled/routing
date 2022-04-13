import routing
import routing.api
import annotate
import mediate

"""
router = routing.Router()


@router.middleware
def middleware(call_next, request):
    print("middleware:", request)

    return call_next(request)


@router.route("/say")
def say(message: str):
    print(message)


router("/mount/say", "Hello, World")
"""


class Counter:
    count: int = 0

    @routing.middleware
    def log(self, call_next, request):
        print(request)

        return call_next(request)

    @routing.route("/add")
    def add(self, amount: int = 1) -> None:
        self.count += 1

    @routing.route("/get")
    def get(self) -> int:
        return self.count


counter: Counter = Counter()

routes = routing.api.get_routes(counter)
middleware = routing.api.get_middleware(counter)

router = routing.api.router(counter)
