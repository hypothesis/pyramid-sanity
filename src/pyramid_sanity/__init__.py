"""Main integration into Pyramids automatic configuration hoovering."""

from pyramid.config import PHASE3_CONFIG
from pyramid.interfaces import ITweens

from pyramid_sanity._egress import EgressTweenFactory
from pyramid_sanity._ingress import IngressTweenFactory
from pyramid_sanity._settings import SanitySettings

__all__ = ["includeme"]


def _add_tween(config):
    sanity_settings = config.registry.settings["pyramid_sanity"]
    tweens = config.registry.queryUtility(ITweens)

    if sanity_settings.ingress_required:
        tweens.add_explicit("pyramid_sanity.ingress_tween_factory", IngressTweenFactory)

    if sanity_settings.egress_required:
        for tween_name, tween_factory in tweens.implicit():
            tweens.add_explicit(tween_name, tween_factory)

        # TODO! - `warehouse.sanity` adds this after every individual tween,
        # but I think it only needs to be in once
        tweens.add_explicit(
            "pyramid_sanity.egress_tween_factory", EgressTweenFactory,
        )


def includeme(config):
    """Configure `pyramid_sanity` to run when called with `config.include`."""

    config.registry.settings["pyramid_sanity"] = SanitySettings.from_pyramid_settings(
        config.registry.settings
    )

    # I'm doing bad things, I'm sorry. - dstufft
    config.action(
        ("tween", "pyramid_sanity.tween_factory", True),
        _add_tween,
        args=(config,),
        order=PHASE3_CONFIG,
    )
