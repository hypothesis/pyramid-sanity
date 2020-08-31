import pytest
from pyramid.request import Request


class TestSanity:
    def test_webob_still_raises_for_bad_boundaries(self):
        # Our check for bad form boundaries now replicates the behavior or
        # webob, instead of triggering the failure in webob. We should check to
        # see if the situation remains in webob otherwise they might fix or
        # change it and none of our tests will show it.

        req = Request.blank(
            "/", method="POST", content_type="multipart/form-data; boundary="
        )
        with pytest.raises(ValueError):
            req.POST.get("")
