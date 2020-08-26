from pyramid.tweens import MAIN

from pyramid_sanity._egress import EgressTweenFactory
from pyramid_sanity._ingress import IngressTweenFactory
from pyramid_sanity._settings import SanitySettings

__all__ = ["includeme"]


def includeme(config):
    """Initialize this extension."""
    settings = SanitySettings.from_pyramid_settings(config.registry.settings)

    # Put the settings into the registry so that other parts of the
    # pyramid_sanity code can access them.
    config.registry.settings["pyramid_sanity"] = settings

    if settings.ingress_required:
        # add_tween() with no `under` or `over` arguments will add the tween to
        # the "top" of the app's tween chain by default (so this tween will be
        # called first, before any other tweens).
        #
        # Other tweens that get added later might get added above this tween, but
        # it's up to the app to manage that.
        config.add_tween("pyramid_sanity.IngressTweenFactory")

    if settings.egress_required:
        # add_tween() with `over=MAIN` will add the tween to the "bottom" of
        # the app's tween chain by default (so this tween will be called last,
        # after any other tweens).
        #
        # Other tweens that get added later might get added below this tween,
        # but it's up to the app to manage that.
        config.add_tween("pyramid_sanity.EgressTweenFactory", over=MAIN)
