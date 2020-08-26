from pyramid.tweens import MAIN

from pyramid_sanity._egress import ascii_safe_redirects_tween_factory
from pyramid_sanity._ingress import (
    invalid_form_tween_factory,
    invalid_path_info_tween_factory,
    invalid_query_string_tween_factory,
)
from pyramid_sanity._settings import SanitySettings

__all__ = ["includeme"]


def includeme(config):
    """Initialize this extension."""
    settings = SanitySettings.from_pyramid_settings(config.registry.settings)

    # add_tween() with no `under` or `over` arguments will add the tween to
    # the "top" of the app's tween chain by default (so this tween will be
    # called first, before any other tweens).
    #
    # Other tweens that get added later might get added above this tween, but
    # it's up to the app to manage that.
    if settings.check_form:
        config.add_tween("pyramid_sanity.invalid_form_tween_factory")

    if settings.check_params:
        config.add_tween("pyramid_sanity.invalid_query_string_tween_factory")

    if settings.check_path:
        config.add_tween("pyramid_sanity.invalid_path_info_tween_factory")

    if settings.ascii_safe_redirects:
        # add_tween() with `over=MAIN` will add the tween to the "bottom" of
        # the app's tween chain by default (so this tween will be called last,
        # after any other tweens).
        #
        # Other tweens that get added later might get added below this tween,
        # but it's up to the app to manage that.
        config.add_tween("pyramid_sanity.ascii_safe_redirects_tween_factory", over=MAIN)
