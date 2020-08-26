# @tween_factory confuses PyLint about function arguments:
# pylint:disable=no-value-for-parameter

import pytest

from pyramid_sanity import ascii_safe_redirects_tween_factory


class TestASCIISafeRedirectsTween:
    def test_it_leaves_non_redirect_responses_alone(self, tween, request, response):
        response = tween(request)

        assert response.location is None

    def test_it_leaves_ascii_redirects_alone(self, tween, request, response):
        response.location = "/a/b/c"

        response = tween(request)

        assert response.location == "/a/b/c"

    def test_it_encodes_unicode_redirects(self, tween, request, response):
        response.location = "/€/☃"

        response = tween(request)

        assert response.location == "/%E2%82%AC/%E2%98%83"

    @pytest.fixture
    def tween(self, handler, registry):
        return ascii_safe_redirects_tween_factory(handler, registry)
