from unittest.mock import create_autospec

import pytest
from pyramid.request import Request

from pyramid_sanity._ingress import IngressTweenFactory
from pyramid_sanity.exceptions import (
    InvalidFormData,
    InvalidQueryString,
    InvalidURL,
    SanityException,
)


def make_check(raises=None):
    check = create_autospec(lambda handler: None)  # pragma: no cover
    if raises:
        check.side_effect = raises

    return check


ALL_CHECKS = (
    IngressTweenFactory.check_invalid_form,
    IngressTweenFactory.check_invalid_query_string,
    IngressTweenFactory.check_invalid_path_info,
)


class TestIngressTweenFactory:
    def test_plain_initialisation(self, handler, registry):
        tween = IngressTweenFactory(handler, registry)

        assert tween.handler == handler
        assert tween.checks == list(ALL_CHECKS)

    @pytest.mark.parametrize(
        "config_setting,check_position",
        (("check_form", 0), ("check_params", 1), ("check_path", 2),),
    )
    def test_disabling_parts(
        self, sanity_settings, config_setting, check_position, handler, registry,
    ):  # pylint: disable=too-many-arguments
        setattr(sanity_settings, config_setting, False)

        tween = IngressTweenFactory(handler, registry)

        checks = list(ALL_CHECKS)
        checks.pop(check_position)
        assert tween.checks == checks

    def test_tween_calls_the_checkers(self, tween, pyramid_request):
        tween.checks = [make_check(), make_check()]

        tween(pyramid_request)

        for check in tween.checks:
            check.assert_called_once_with(pyramid_request)

    def test_tween_calls_handler(self, tween, pyramid_request):
        response = tween(pyramid_request)

        tween.handler.assert_called_once_with(pyramid_request)
        assert response == tween.handler.return_value

    def test_tween_returns_exception_if_check_raises_SanityException(
        self, tween, pyramid_request
    ):
        check = make_check(raises=SanityException("Terrible news"))
        tween.checks = [check]

        response = tween(pyramid_request)

        assert response == check.side_effect

    def test_tween_raises_if_check_raises_normal_error(self, tween, pyramid_request):
        tween.checks = [make_check(raises=ValueError("Terrible news"))]

        with pytest.raises(ValueError):
            tween(pyramid_request)

    @pytest.fixture
    def tween(self, handler, registry):
        return IngressTweenFactory(handler, registry)


class TestChecks:
    def test_check_invalid_query_string_ok(self):
        IngressTweenFactory.check_invalid_query_string(Request.blank("/?a=1"))

    def test_check_invalid_query_string(self):
        request = Request.blank("/?f%FC=123")

        with pytest.raises(InvalidQueryString):
            IngressTweenFactory.check_invalid_query_string(request)

    def test_check_invalid_path_info_ok(self):
        IngressTweenFactory.check_invalid_path_info(Request.blank("/a/b"))

    def test_check_invalid_path_info(self):
        request = Request.blank("/%BF%B")

        with pytest.raises(InvalidURL):
            IngressTweenFactory.check_invalid_path_info(request)

    def test_check_invalid_form_ok(self):
        IngressTweenFactory.check_invalid_form(
            Request.blank(
                "/",
                method="POST",
                content_type="multipart/form-data; boundary=239487389475",
            )
        )

    def test_check_invalid_form(self):
        request = Request.blank("/", method="POST", content_type="multipart/form-data")

        with pytest.raises(InvalidFormData):
            IngressTweenFactory.check_invalid_form(request)
