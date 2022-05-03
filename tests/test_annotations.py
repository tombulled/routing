import annotate
from routing import annotations, enums, models


def test_route() -> None:
    @annotations.route("foo")
    def foo():
        pass

    assert annotate.get_annotations(foo) == {
        enums.Annotation.ROUTE: [models.Route("foo")]
    }


def test_middleware() -> None:
    @annotations.middleware
    def foo():
        pass

    assert enums.Annotation.MIDDLEWARE in annotate.get_annotations(foo)
