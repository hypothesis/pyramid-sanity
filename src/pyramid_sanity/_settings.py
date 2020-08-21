"""Logic for reading settings from `pyramid_settings`."""

from pyramid.settings import asbool


class SanitySettings:
    """Configuration for all `pyramid_sanity` settings."""

    ascii_safe_redirects = True
    check_form = True
    check_params = True
    check_path = True

    BOOLEAN_FIELDS = (
        "ascii_safe_redirects",
        "check_form",
        "check_params",
        "check_path",
    )

    def all_off(self):
        """Disable all options."""

        for field in self.BOOLEAN_FIELDS:
            setattr(self, field, False)

    @classmethod
    def from_pyramid_settings(cls, settings):
        """Load configuration from the provided settings.

        :param settings: A settings mapping, e.g. `registry.settings`
        :return: A SanitySettings with the correct parameters set
        """
        config = SanitySettings()

        if asbool(settings.get("pyramid_sanity.disable_all", False)):
            config.all_off()

        for key in cls.BOOLEAN_FIELDS:
            value = settings.get(f"pyramid_sanity.{key}", ...)
            if value is not ...:
                setattr(config, key, asbool(value))

        return config

    @property
    def egress_required(self):
        """Get whether any egress options are enabled."""
        return self.ascii_safe_redirects

    @property
    def ingress_required(self):
        """Get whether any ingress options are enabled."""
        return any((self.check_form, self.check_params, self.check_path))
