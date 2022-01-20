import routing

router = routing.Router()

@router.route('turn {direction}')
def turn(direction: str):
    return f'Turn: {direction}'

print(router('turn left'))
