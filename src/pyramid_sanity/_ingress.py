"""Define tweens that check data on the way into Pyramid."""

from pyramid_sanity.exceptions import (
    InvalidFormData,
    InvalidQueryString,
    InvalidURL,
    SanityException,
)


class IngressTweenFactory:
    """Generate a tween for checking values on the way into Pyramid."""

    def __init__(self, handler, registry):
        self.handler = handler
        self.checks = list(self.get_checks(registry.settings["pyramid_sanity"]))

    def __call__(self, request):
        """Handle the request as a tween."""

        for check in self.checks:
            try:
                check(request)
            except SanityException as exc:
                return exc

        return self.handler(request)

    @classmethod
    def get_checks(cls, sanity_settings):
        """Get the correct handlers based on the provided settings.

        :param sanity_settings: An instance of Configuration
        :returns: A generator of checks to apply to a request
        :rtype: Functions which accept `request` as a single parameter
        """
        if sanity_settings.check_form:
            yield cls.check_invalid_form

        if sanity_settings.check_params:
            yield cls.check_invalid_query_string

        if sanity_settings.check_path:
            yield cls.check_invalid_path_info

    @classmethod
    def check_invalid_form(cls, request):
        """Catch errors relating to poorly formatted POST form data.

        :raise InvalidFormData: When any error is encountered
        """

        # Ref: https://github.com/Pylons/pyramid/issues/1258

        if request.method == "POST":
            try:
                request.POST.get("", None)
            except ValueError as err:
                raise InvalidFormData("Invalid form data") from err

    @classmethod
    def check_invalid_query_string(cls, request):
        """Catch errors relating to poorly encoded URL parameters.

        :raise InvalidQueryString: When any error is encountered
        """

        # Ref: https://github.com/Pylons/webob/issues/161
        # Ref: https://github.com/Pylons/webob/issues/115

        try:
            request.GET.get("", None)
        except UnicodeDecodeError as err:
            raise InvalidQueryString("Invalid bytes in query string") from err

    @classmethod
    def check_invalid_path_info(cls, request):
        """Check for look for invalid UTF-8 bytes in a path.

        :raise InvalidURL: When any error is encountered
        """

        # Ref: https://github.com/Pylons/pyramid/issues/434

        try:
            request.path_info
        except UnicodeDecodeError as err:
            raise InvalidURL("Invalid bytes in URL") from err
