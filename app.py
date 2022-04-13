import routing

router = routing.Router()


@router.middleware
def only_eat_pizza(call_next, request):
    request.args = routing.Arguments("pizza")

    return call_next(request)


@router.route("eat {food}")
def eat(food):
    print(f"Eating: {food}")
