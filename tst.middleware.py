import routing
import routing.middleware

router = routing.Router()

router.middleware(routing.middleware.parametrise)

@router.middleware
def feed_params(request, call_next):
    request.params.distance = 100
    
    return call_next(request)

@router.route('move {distance:d}')
def move(distance: int):
    return f'Move: {distance}'
