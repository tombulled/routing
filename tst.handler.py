import routing

router = routing.Router()

@router.route('turn {direction}')
def turn(request):
    return f'Turn: {request.params.direction}'

@router.route('move {distance:d}')
@routing.handler
def move(distance: int):
    return f'Move: {distance}'
