# @tween_factory confuses PyLint about function arguments:
# pylint:disable=no-value-for-parameter

import pytest
from pyramid.request import Request

from pyramid_sanity.exceptions import InvalidFormData, InvalidQueryString, InvalidURL
from pyramid_sanity.tweens import (
    ascii_safe_redirects_tween_factory,
    invalid_form_tween_factory,
    invalid_path_info_tween_factory,
    invalid_query_string_tween_factory,
)


class SharedTests:
    """Shared tests that apply to all tweens."""

    def test_it_does_nothing_for_valid_requests(self, handler, tween):
        # A request with a valid path, query string and form body.
        req = Request.blank(
            "/a/b?a=1",
            method="POST",
            content_type="multipart/form-data; boundary=239487389475",
        )

        response = tween(req)

        handler.assert_called_once_with(req)
        assert response == handler.return_value


class TestInvalidFormTween(SharedTests):
    GOOD_MULTIPART = "multipart/form-data; boundary=valid-boundary-------"
    BAD_MULTIPART = "multipart/form-data; boundary="

    def test_it_returns_InvalidFormData_for_invalid_form_post_requests(self, tween):
        req = Request.blank("/", method="POST", content_type=self.BAD_MULTIPART)

        result = tween(req)

        assert isinstance(result, InvalidFormData)

    def test_it_does_not_consume_the_post_body_iterator(self, tween):
        req = Request.blank(
            "/", method="POST", content_type=self.GOOD_MULTIPART, POST="content"
        )

        tween(req)

        # pylint: disable=compare-to-zero
        assert req.body_file_raw.tell() == 0
        assert req.body_file.tell() == 0

    @pytest.mark.parametrize(
        "option,value",
        (
            ("method", "GET"),
            ("content_type", "other"),
            # Some things considered forms by webob, but not multipart
            ("content_type", ""),
            ("content_type", "application/x-www-form-urlencoded"),
        ),
    )
    def test_it_does_nothing_for_other_requests(self, handler, tween, option, value):
        defaults = dict(method="POST", content_type=self.GOOD_MULTIPART)
        defaults[option] = value

        req = Request.blank("/any", **defaults)

        response = tween(req)

        handler.assert_called_once_with(req)
        assert response == handler.return_value

    @pytest.fixture
    def tween(self, handler, registry):
        return invalid_form_tween_factory(handler, registry)


class TestInvalidQueryStringTween(SharedTests):
    def test_it_returns_InvalidQueryString_for_requests_with_invalid_query_strings(
        self, tween
    ):
        req = Request.blank("/?f%FC=123")

        result = tween(req)

        assert isinstance(result, InvalidQueryString)

    @pytest.fixture
    def tween(self, handler, registry):
        return invalid_query_string_tween_factory(handler, registry)


class TestInvalidPathInfoTween(SharedTests):
    def test_it_returns_InvalidURL_for_requests_with_invalid_paths(self, tween):
        req = Request.blank("/%BF%B")

        result = tween(req)

        assert isinstance(result, InvalidURL)

    @pytest.fixture
    def tween(self, handler, registry):
        return invalid_path_info_tween_factory(handler, registry)


class TestASCIISafeRedirectsTween(SharedTests):
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
