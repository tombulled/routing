import routing

router = routing.HttpRouter(middleware=[])


@router.any("/hello/{name}")
def hello(name):
    return f"Hello, {name}"


d = router("/hello/bob", method="gurgle")
