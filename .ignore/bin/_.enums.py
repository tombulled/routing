import enumb

# https://datatracker.ietf.org/doc/html/rfc7231#section-4.3
class Method(enumb.Upper):
    PUT:     str
    GET:     str
    POST:    str
    HEAD:    str
    PATCH:   str
    DELETE:  str
    OPTIONS: str
