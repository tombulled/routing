# routing
Routing for Python

## Example: Basic
```python
import routing

router = routing.Router()

@router.route('hello')
def hello():
    print('Hello!')
```

```python
>>> router('hello')
Hello!
```

## Example: Passing Arguments
```python
import routing

router = routing.Router()

@router.route('say')
def say(message):
    print(message)
```

```python
>>> router('say', 'Hello, World')
Hello, World
```

## Example: Path Parameters
```python
import routing

router = routing.Router()

@router.route('turn {direction}')
def turn(direction):
    print(f'Turning: {direction}')
```

```python
>>> router('turn left')
Turning: left
```

## Example: Middleware
```python
import routing

router = routing.Router()

@router.middleware
def only_eat_pizza(call_next, request):
    request.args = routing.Arguments('pizza')

    return call_next(request)

@router.route('eat {food}')
def eat(food):
    print(f'Eating: {food}')
```

```python
>>> router('eat vegetables') 
Eating: pizza
```