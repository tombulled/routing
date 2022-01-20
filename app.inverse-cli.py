import routing

router = routing.InverseRouter()

router.route('turn {direction}')()

r = router('turn {direction}')(direction = 'right')
