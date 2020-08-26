"""Define tweens that check data on the way out of Pyramid."""

import urllib.parse

from pyramid_sanity._ingress import tween_factory


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
