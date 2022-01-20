import routing

router = routing.HttpRouter()

@router.any('/hello/{name}')
def hello(request):
    print(request)
    return f'Hello {request.params.name}'

d = router('/hello/tom', method='get')
d2 = router(router.routes[0], method='get')
d3 = router(routing.Request(path='/hello/{name}', params={'name': 'Bob'}))
