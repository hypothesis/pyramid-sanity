"""All exceptions raised by `pyramid_sanity`."""

# pylint: disable=too-many-ancestors

from pyramid.httpexceptions import HTTPBadRequest


class SanityException(HTTPBadRequest):
    """Base exception for all sanity based problems."""


class InvalidQueryString(SanityException):
    """The query string contains errors."""


class InvalidFormData(SanityException):
    """The form data contains errors."""


class InvalidURL(SanityException):
    """The URL contains errors."""
