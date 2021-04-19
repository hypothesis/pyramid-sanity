import pytest
from pyramid.request import Request
from pytest import param


class TestFailureConditions:
    """Test expected failure conditions in underlying frameworks still exist.

    We rely on frameworks to raise certain errors for us to prevent them. We
    should test to see the errors conform to our understanding and still exist.

    This will give us some notice if maintainers fix or change the behavior.
    """

    def test_webob_raises_for_bad_params(self):
        with pytest.raises(UnicodeDecodeError):
            Request.blank("/?f%FC=123").GET.get("")

    def test_webob_raises_for_bad_url(self):
        with pytest.raises(UnicodeDecodeError):
            assert Request.blank("/%BF%B").url

    def test_webob_raises_for_bad_boundaries(self):
        req = Request.blank("/", method="POST", content_type="multipart/form-data")
        with pytest.raises(ValueError):
            req.POST.get("")

    def test_webob_does_not_raise_for_non_multipart_types(self, non_multipart_types):
        req = Request.blank("/", method="POST", content_type=non_multipart_types)
        req.POST.get("")

    @pytest.fixture(
        params=[param("", id="*blank*"), "application/x-www-form-urlencoded"],
    )
    def non_multipart_types(self, request):
        return request.param
