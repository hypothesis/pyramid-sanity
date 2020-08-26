from unittest import mock
from unittest.mock import create_autospec

import pytest
from pyramid import testing
from pyramid.response import Response


@pytest.fixture
def response():
    return Response()


@pytest.fixture
def handler(response):
    handler = create_autospec(lambda request: None)  # pragma: no cover
    handler.return_value = response

    return handler


@pytest.fixture
def pyramid_request():
    return testing.DummyRequest()


@pytest.fixture
def pyramid_config(pyramid_request):
    with testing.testConfig(request=pyramid_request, settings={}) as config:
        with mock.patch.object(config, "add_tween", auto_spec=True):
            yield config


@pytest.fixture
def registry(pyramid_config):
    return pyramid_config.registry


@pytest.fixture
def patch(request):  # pragma:nocover
    def autopatcher(target):
        """Patch and cleanup automatically. Wraps :py:func:`mock.patch`."""

        patcher = mock.patch(target, autospec=True)
        patched_object = patcher.start()
        request.addfinalizer(patcher.stop)

        return patched_object

    return autopatcher
