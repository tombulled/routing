import routing

router = routing.Router()


@router.middleware
def negate(request, call_next):
    request.params.adjective = f"not {request.params.adjective}"

    return call_next(request)


@router.route("declare {name} as {adjective}")
def declare(name: str, adjective: str):
    return f"Declaration: {name} is {adjective}"


d = router("declare judith as awesome")
