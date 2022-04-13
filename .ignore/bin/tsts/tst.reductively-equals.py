import routing

p = routing.Path("/user/{name}")
p2 = routing.Path("/user/{username}")
p3 = routing.Path("/User/{name}")

eq = p.reductively_equals(p3, case_sensitive=False)
eq2 = p.matches("/User/Bob")
eq3 = p.reductively_equals(p3, case_sensitive=True)
