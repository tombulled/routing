import routing
import routing.sentinels

import dataclasses
import inspect

import label
import sentinel

'''
Supported path types:
    int (concatenates)
    str (concatenates)
    
    other: float, list, tuple, dict, set

Notes:
    * Implement descriptors?
    * Implement mounts

mult_2 = router()

mult_2.route(1)(2)
mult_2.route(2)(4)
mult_2.route(3)(6)

class Api(Router):
    class Users(Router):
        @route('/user')
        def users(self):
            return []

@controller
class UserController:
    @get('/')
    def index() -> str:
        return 'Hello, World!'

-----

@component
class User:
    id: int
    name: str

@configuration
@profile('dev')
class Config:
    @bean
    def redis() -> Redis:
        return Redis(...)

@application
class Application:
    db: Redis = autowired()

E.g. with innertube, use a settings.toml
'''

# GLOBAL_ROUTER = Router()
#
# route = GLOBAL_ROUTER.route

# @routing.mount('/say')
# @routing.route('/hi')
# @routing.route('/hello')
# def hello(name: str):
#     print(f'Hello, {name}')

# class Account:
#     secret: str = 'carrot-stick'
#
#     @route('/foo')
#     def foo(self):
#         print('foo:', self)
#
# account = Account()
#
# # @mount('/ai')
# @route('/learn')
# def learn():
#     print('Learning!')
#
# # @mount('/api')
# @router
# class Api:
#     @route('/login')
#     def login(self, username: str, password: str) -> None:
#         print(f'Login: {username!r}, {password!r}')

@dataclasses.dataclass
class Counter:
    count: int = 0

    @routing.route('/add', '/increment')
    def add(self) -> None:
        self.count += 1

    @routing.route('/get', '/value')
    def get(self) -> int:
        return self.count

router = routing.router(Counter(50))

@routing.route('/foo')
def foo(): return 'foo'

r = routing.Router()

@r.route('/bar')
def bar(): return 'bar'

@r.middleware
def process(call_next):
    return call_next()

# @routing.mount('/api')
# @routing.router
# class Api:
#     db: dict = dataclasses.field(default_factory = dict)
#
#     @routing.router
#     class Users:
#         users: list = dataclasses.field(default_factory = list)
#
#         @routing.route('/user')
#         def list(self):
#             return self.users
#
#         @routing.route('/user/{id}')
#         def user(self, id):
#             for user in self.users:
#                 if user['id'] == id:
#                     return user
#
#     @routing.router
#     class Courses:
#         @routing.route('/courses')
#         def courses(self):
#             return []
#
#         @routing.route('/course/{id}')
#         def course(self, id):
#             return None

# Middleware added to 'root' router
# @routing.middleware
# def process(request, call_next):
#     # mess with request here
#
#     return call_next(request)
#
# router_a = routing.Router()

# Middleware added to 'router_a' router
# @router_a.middleware
# def process(request, call_next):
#     # mess with request here
#
#     return call_next(request)

# class RouterB:
#     # Middleware added to RouterB
#     @routing.middleware
#     def process(request, call_next):
#         # mess with request here
#
#         return call_next(request)

# @routing.route('/foo')
# class Foo:
#     def __call__(self):
#         print('Foo!')

# r = Router()
#
# @r.route('/')
# def root():
#     print('Root1!')
#
# x = r.route('/foo')
#
# def foo():pass
# x(1)

# router = routing.Router()
#
# router['/login'] = lambda username, password: 'Logged in!'
