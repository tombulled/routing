import routing

router = routing.InverseHttpRouter()

router.get('/hello/{name}')()

def foo(request): pass
    return lambda *, name: request.copy \
    (
        params = dict \
        (
            name = name,
        ),
    )

# @router.any('/hello')
# def bar(request):
#     return lambda method: request.copy \
#     (
#         method = method,
#     )
#
# @router.get('/user/{id}/name', '/user/{id}/age')
# def baz(request):
#     return lambda id: request.copy \
#     (
#         params = dict \
#         (
#             id = id,
#         ),
#     )

r  = router('/hello/{name}', method='get')(name = 'tom')
# r2 = router('/hello', method='anything')('post')
# r3 = router('/user/{id}/age', method='get')(123)
