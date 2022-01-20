import routing

router = routing.HttpRouter()

@router.post('/deposit/{amount:d}')
def deposit(amount: int):
    return f'Deposit: {amount}'

d = router('/deposit/123', method='post')
