import pytest
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from webtest.app import TestApp as WebTestApp


class BrokenWebTestApp(WebTestApp):
    def encode_multipart(self, params, files):
        content_type, body = super().encode_multipart(params, files)

        # Return some nonsense to break form parsing. We should have a boundary
        # but we don't
        content_type = "multipart/form-data; boundary="

        return content_type, body


class TestIntegration:
    def test_happy_path(self, app):
        response = app.get("/redirect")

        assert response.status_code == 302

    def test_broken_unicode_redirect(self, app):
        # The AssertionError here is actually coming from webtest
        with pytest.raises(AssertionError):
            app.get("/bad-redirect")

    @pytest.mark.usefixtures("with_sanity")
    def test_fixed_unicode_redirect(self, app):
        response = app.get("/bad-redirect")

        assert (
            response.location
            == "http://localhost/http%3A/example.com/%E2%82%AC/%E2%98%83"
        )

    def test_broken_query_param_encoding(self, app):
        with pytest.raises(ValueError):
            app.get("/redirect?f%FC=123")

    @pytest.mark.usefixtures("with_sanity")
    def test_handled_query_param_encoding(self, app):
        app.get("/redirect?f%FC=123", status=400)

    def test_broken_url_encoding(self, app):
        with pytest.raises(ValueError):
            app.get("/%BF%B")

    @pytest.mark.usefixtures("with_sanity")
    def test_handled_url_encoding(self, app):
        app.get("/%BF%B", status=400)

    def test_broken_form_data_declaration(self, app):
        # The BrokenWebTestApp determines our content type. What we put here
        # is only used to determine we are trying to do multipart, then it
        # get's replaced
        with pytest.raises(ValueError):
            app.post("/redirect", content_type="multipart/form-data", params="\0")

    @pytest.mark.usefixtures("with_sanity")
    def test_handled_form_data_declaration(self, app):
        app.post(
            "/redirect", content_type="multipart/form-data", params="\0", status=400
        )

    @pytest.fixture
    def with_sanity(self, config):
        config.include("pyramid_sanity")

    @pytest.fixture
    def config(self):
        return Configurator()

    @pytest.fixture
    def app(self, config):
        def redirect(request):
            request.GET.get("", None)
            request.POST.get("", None)
            return HTTPFound(location="http://example.com")

        def bad_redirect(_request):
            return HTTPFound(location="http://example.com/€/☃")

        config.add_route("redirect", "/redirect")
        config.add_route("bad_redirect", "/bad-redirect")

        config.add_view(redirect, route_name="redirect")
        config.add_view(bad_redirect, route_name="bad_redirect")

        return BrokenWebTestApp(config.make_wsgi_app())
