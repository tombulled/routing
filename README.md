# routing

### Example: Basic Routing
```python
import routing

router = routing.Router()

@router.route('turn {direction}')
def turn(request):
    return f'Turn: {request.params.direction}'
```

#### Usage:
```python
>>> router('turn left')
'Turn: left'
>>>
```

<br>

### Example: HTTP Routing
...
