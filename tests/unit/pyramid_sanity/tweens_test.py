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
    def test_it_returns_InvalidFormData_for_invalid_form_post_requests(
        self, tween, form_type
    ):
        self.assert_raises_for_content_type(tween, content_type=form_type)

    @pytest.mark.usefixtures("assume_form_on")
    def test_it_returns_InvalidFormData_for_invalid_blank_content_type_when_enabled(
        self, tween
    ):
        self.assert_raises_for_content_type(tween, content_type="")

    def test_it_does_not_consume_the_post_body_iterator(self, tween, form_type):
        req = Request.blank(
            "/",
            method="POST",
            content_type=f"{form_type}; boundary=valid-boundary-------",
            POST="content",
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
            # By default a blank content type is not assumed to be a form
            ("content_type", ""),
        ),
    )
    def test_it_does_nothing_for_other_requests(self, handler, tween, option, value):
        options = dict(
            method="POST", content_type="multipart/form-data; boundary=239487389475"
        )
        options[option] = value

        req = Request.blank("/any", **options)

        response = tween(req)

        handler.assert_called_once_with(req)
        assert response == handler.return_value

    def assert_raises_for_content_type(self, tween, content_type):
        req = Request.blank("/", method="POST", content_type=content_type)

        result = tween(req)

        assert isinstance(result, InvalidFormData)

    @pytest.fixture(
        params=["multipart/form-data", "application/x-www-form-urlencoded"],
    )
    def form_type(self, request):
        return request.param

    @pytest.fixture
    def assume_form_on(self, registry):
        registry.settings["pyramid_sanity.check_form.assume_form_on_blank"] = True

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
