"""Pyramid tweens."""

# All tweens return the request object, so we don't want to have to document
# that in every docstring in this file.
# pylint:disable=missing-return-doc

import cgi
import urllib.parse
from functools import wraps

from pyramid.settings import asbool

from pyramid_sanity.exceptions import (
    InvalidFormData,
    InvalidQueryString,
    InvalidURL,
    SanityException,
)


def tween_factory(check):
    """Create a tween factory from the provided function.

    The function will be called with: (request, handler, registry).

    If the function raises SanityException or any SanityException subclass the
    exception will be caught and *returned* instead of raised. This is because
    if a tween raises an HTTPException that skips Pyramid exception views,
    whereas if a tween *returns* an HTTPException then any matching exception
    view *does* get called.
    """

    @wraps(check)
    def factory(handler, registry):
        def tween(request):
            try:
                return check(request, handler, registry)
            except SanityException as err:
                return err

        return tween

    return factory


@tween_factory
def invalid_form_tween_factory(request, handler, registry):
    """Catch errors relating to poorly formatted POST form data.

    :raise InvalidFormData: if there is poorly-formatted POST form data
    """

    # Check the form boundary without consuming the body
    if request.method == "POST":
        assume_form = asbool(
            registry.settings.get(
                "pyramid_sanity.check_form.assume_form_on_blank", False
            )
        )
        _check_form_boundary(request, assume_form=assume_form)

    return handler(request)


def _check_form_boundary(request, assume_form=False):
    """Replicate the webob.compat PY3 exception for parsing headers.

    :param request: Pyramid request to check
    :param assume_form: Assume a form type when the content type is blank
    :raise InvalidFormData: If an invalid boundary is found
    """

    content_type = request.headers.get("Content-Type")
    if not content_type and assume_form:
        content_type = "multipart/form-data"

    content_type, options = cgi.parse_header(content_type or "")

    # The types webob.request counts as form submissions (minus "" which is
    # effectively enabled by setting `assume_form=True`)
    if content_type not in (
        "application/x-www-form-urlencoded",
        "multipart/form-data",
    ):
        return

    if not cgi.valid_boundary(options.get("boundary", "")):
        raise InvalidFormData(
            "Invalid form data: no boundary specified in Content-Type"
        )


@tween_factory
def invalid_query_string_tween_factory(request, handler, _registry):
    """Catch errors relating to poorly encoded query parameters.

    :raise InvalidQueryString: if there are poorly encoded query params
    """
    try:
        request.GET.get("", None)
    except UnicodeDecodeError as err:
        raise InvalidQueryString("Invalid bytes in query string") from err

    return handler(request)


@tween_factory
def invalid_path_info_tween_factory(request, handler, _registry):
    """Check for look for invalid UTF-8 bytes in the request path.

    :raise InvalidURL: if there are invalid UTF-8 bytes in the request path
    """
    try:
        request.path_info
    except UnicodeDecodeError as err:
        raise InvalidURL("Invalid bytes in URL") from err

    return handler(request)


@tween_factory
def ascii_safe_redirects_tween_factory(request, handler, _registry):
    """Ensure redirects are ASCII safe."""
    response = handler(request)

    if response.location:
        try:
            response.location.encode("ascii")
        except UnicodeEncodeError:
            response.location = "/".join(
                [urllib.parse.quote_plus(part) for part in response.location.split("/")]
            )

    return response
