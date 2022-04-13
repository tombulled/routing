import routing

router = routing.Router()

router.route("data")(routing.Target({"username": "foo", "password": "bar"}))

data = router("data")

print(data)
