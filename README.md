# routing

## Example: Basic Routing

### Implementation:
```python
import routing

router = routing.Router()

@router.route('turn {direction}')
def turn(direction: str):
    return f'Turn: {direction}'
```

### Usage:
```python
>>> router('turn left')
'Turn: left'
>>>
```

<br>

## Example: Basic HTTP Routing

### Implementation:
```python
import routing

router = routing.HttpRouter()

@router.post('/deposit/{amount:d}')
def deposit(amount: int):
    return f'Deposit: {amount}'
```

### Usage:
```python
>>> router('/deposit/123', method='post')
'Deposit: 123'
>>>
```

<br>

## Example: Advanced Routing

### Implementation:
```python
import routing

router = routing.Router()

@router.middleware
def negate(request, call_next):
    request.params.adjective = f'not {request.params.adjective}'

    return call_next(request)

@router.route('declare {name} as {adjective}')
def declare(name: str, adjective: str):
    return f'Declaration: {name} is {adjective}'
```

### Usage:
```python
>>> declare('judith', 'awesome')
'Declaration: judith is not awesome'
>>>
```

<br>

## Example: Inverse Basic Routing

### Implementation:
```python
import routing

router = routing.Router()

router.route('turn {direction}')()
```

### Usage:
```python
>>> router('turn {direction}')(direction = 'right')
Request(path='turn {direction}', params={'direction': 'right'})
>>>
```

<br>

## Example: Inverse HTTP Routing

### Implementation:
```python
import routing

router = routing.InverseHttpRouter()

router.get('/hello/{name}')()
```

### Usage:
```python
>>> router('/hello/{name}', method='get')(name = 'sam')
HttpRequest(path='/hello/{name}', params={'name': 'sam'}, method='get')
>>>
```
