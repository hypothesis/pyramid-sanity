from pyramid.tweens import MAIN

from pyramid_sanity._egress import EgressTweenFactory
from pyramid_sanity._ingress import IngressTweenFactory
from pyramid_sanity._settings import SanitySettings


def includeme(config):
    settings = SanitySettings.from_pyramid_settings(config.registry.settings)

    # Put the settings into the registry so that other parts of the
    # pyramid_sanity code can access them.
    config.registry.settings["pyramid_sanity"] = settings

    if settings.ingress_required:
        config.add_tween("pyramid_sanity.IngressTweenFactory")

    if settings.egress_required:
        config.add_tween("pyramid_sanity.EgressTweenFactory", over=MAIN)
