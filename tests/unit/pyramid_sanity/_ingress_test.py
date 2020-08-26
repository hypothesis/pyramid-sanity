# @tween_factory confuses PyLint about function arguments:
# pylint:disable=no-value-for-parameter

import pytest
from pyramid.request import Request

from pyramid_sanity._ingress import (
    invalid_form_tween_factory,
    invalid_path_info_tween_factory,
    invalid_query_string_tween_factory,
)
from pyramid_sanity.exceptions import InvalidFormData, InvalidQueryString, InvalidURL


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
    def test_it_returns_InvalidFormData_for_invalid_form_post_requests(self, tween):
        req = Request.blank("/", method="POST", content_type="multipart/form-data")

        result = tween(req)

        assert isinstance(result, InvalidFormData)

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
