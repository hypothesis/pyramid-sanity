import functools
from unittest import mock
from unittest.mock import create_autospec

import pytest
from pyramid.registry import Registry
from pyramid.request import Request
from pyramid.response import Response

from pyramid_sanity._settings import SanitySettings


@pytest.fixture
def pyramid_request():
    return create_autospec(Request, instance=True)


@pytest.fixture
def registry(sanity_settings):
    registry = Registry()
    registry.settings = {"pyramid_sanity": sanity_settings}

    return registry


@pytest.fixture
def handler(response):
    handler = create_autospec(lambda request: None)  # pragma: no cover
    handler.return_value = response

    return handler


@pytest.fixture
def response():
    return Response()


@pytest.fixture
def sanity_settings():
    return SanitySettings()


@pytest.fixture
def patch(request):
    def autopatcher(target):
        """Patch and cleanup automatically. Wraps :py:func:`mock.patch`."""

        patcher = mock.patch(target, autospec=True)
        patched_object = patcher.start()
        request.addfinalizer(patcher.stop)

        return patched_object

    return autopatcher
