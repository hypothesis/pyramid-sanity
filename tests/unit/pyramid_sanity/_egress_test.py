import pytest

from pyramid_sanity import EgressTweenFactory


class TestEgressTweenFactory:
    def test_initialisation(self, handler, registry):
        tween = EgressTweenFactory(handler, registry)

        assert tween.handler == handler

    def test_it_calls_the_handler(self, tween, request):
        response = tween(request)

        tween.handler.assert_called_once_with(request)
        assert response == tween.handler.return_value


class TestChecks:
    def test_it_leaves_ascii_redirects_alone(self, tween, request, response):
        response.location = "/a/b/c"

        response = tween(request)

        assert response.location == "/a/b/c"

    def test_it_encodes_unicode_redirects(self, tween, request, response):
        response.location = "/€/☃"

        response = tween(request)

        assert response.location == "/%E2%82%AC/%E2%98%83"


@pytest.fixture
def tween(handler, registry):
    return EgressTweenFactory(handler, registry)
