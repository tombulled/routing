# routing

## Example: Basic Routing

### Implementation:
```python
import routing

router = routing.Router()

@router.route('turn {direction}')
def turn(request):
    return f'Turn: {request.params.direction}'
```

### Usage:
```python
>>> router('turn left')
'Turn: left'
>>>
```

<br>

## Example: HTTP Routing

### Implementation:
```python
import routing

router = routing.HttpRouter()

@router.get('/hello/{name}')
def foo(request):
    return f'Hello {request.params.name}'
```

### Usage:
```python
>>> router('/hello/peter', method='get')
'Hello peter'
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
