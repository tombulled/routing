import routing

'''
TODO:
    * Implement <Mount>?
        * What about a suffix mount???
            e.g. /hello/{name}, /go-away/{name} ?

            e.g:
                @route('north {distance}', 'south {distance}', 'east {distance}')
    * Implement partial <Request>s?
        E.g:
            @router.route('/foo')
            def foo(request):
                return lambda: request.copy(method='get')

            router('/foo')()
    * Any way to improve HttpRoute having a dependency on HttpMethodRouter?
        E.g. By separating out to separate modules routing.basic, routing.http?
    * Test instantiating all at once
        E.g: Router(routes=[Route(...), ...])
    * For inverse routers pass a 'spec' that has a .request() method that functions like .copy()?
    * Make the parse.parser an attribute so it can be modified (set in __init__)
        E.g. whether /foo/{bar} should match /foo/bar/cat?
        Is this an attribute of the router or path?
            This should take on responsibility of `case_sensitive`?
            Adds support for custom formatters (`extra_types`?)
        Passed as a config item on the router, e.g:
            router = Router(parser = SomeCustomParser)
    * Create a <Router> interface:
        .__call__, .route, .middleware?, .resolve etc.
    * Add simple example to proxy requests to httpbin
    * Allow inverse routing to add routes without second call:
        router = InverseHttpRouter()

        router.get('/user/name')
        router.post('/user/age')
        router.put('/user/age/{age}')
    * Make inverse routers return the route/target: (But what about multiple routes)
        router = InverseRouter()

        turn = router.route('turn {direction}', name='turn')

        request = turn(direction='left')
        # Equivelant to:
        request = router('turn')(direction='left')
    * Add route `name`s, this will aid inverse routers (see above) (But what about multiple routes)
        Route shouldn't have a name, an endpoint should?
    * parameterize shouldn't be middleware, it should be a configuration flag
    * Create a routing client?
    * Only allow one path for inverse routers?
    * Add example for custom routers?
    * Ensure `parse` plays nicely with `enums`
'''

'''
Ideal API:

# Http Router:
router = routing.HttpRouter()

@router.get('/user/{id:d}/age')
def user_age(id: int):
    return 43

# Inverse Http Router:
router = routing.InverseHttpRouter()

@router.post('/login')
def login(request, *, username: str, password: str):
    return request.copy \
    (
        data = dict \
        (
            username = username,
            password = password,
        ),
    )

d = router('/login', method='post')(username='sam', password='bob')
'''

# router = routing.Router()

# route = routing.Route('/users')

# @route
# def users():
#     print('requested users!')

# @router.route('/foo')
# def get_foo():
#     print('get foo!')

# router.route('/foo')
# router.route('/bar')
# router.route('/user/{name}')

# route = router('/foo')()()

# br = routing.BaseRouter()
#
# @br.get
# def foo():
#     print('GET foo()!')
#
# br.bar()
#
# br('get')()

api      = routing.BaseRouter()
complete = routing.BaseRouter()

@complete.route('/search')
def complete_search(q: str):
    print(f'complete_search({q!r})')

api.route('/complete')(complete)
