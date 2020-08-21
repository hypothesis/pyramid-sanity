"""Define tweens that check data on the way out of Pyramid."""

import urllib.parse


class EgressTweenFactory:
    """Generate a tween for checking values coming out of Pyramid."""

    def __init__(self, handler, _registry):
        self.handler = handler

    def __call__(self, request):
        """Handle the request as a tween."""

        return self.ascii_safe_redirects(self.handler(request))

    @classmethod
    def ascii_safe_redirects(cls, response):
        """Ensure redirects are ASCII safe."""

        if response.location:
            try:
                response.location.encode("ascii")
            except UnicodeEncodeError:
                response.location = "/".join(
                    [
                        urllib.parse.quote_plus(part)
                        for part in response.location.split("/")
                    ]
                )

        return response
