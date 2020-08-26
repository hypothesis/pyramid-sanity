from pyramid.settings import asbool
from pyramid.tweens import MAIN


def includeme(config):
    """Initialize this extension."""

    default = not asbool(config.registry.settings.get("pyramid_sanity.disable_all"))

    for setting, tween, options in (
        # add_tween() with no `under` or `over` arguments will add the tween to
        # the "top" of the app's tween chain by default (so this tween will be
        # called first, before any other tweens).
        ("check_form", "invalid_form_tween_factory", {}),
        ("check_params", "invalid_query_string_tween_factory", {}),
        ("check_path", "invalid_path_info_tween_factory", {}),
        # add_tween() with `over=MAIN` will add the tween to the "bottom" of
        # the app's tween chain by default (so this tween will be called last,
        # after any other tweens).
        ("ascii_safe_redirects", "ascii_safe_redirects_tween_factory", {"over": MAIN}),
    ):
        tween_enabled = asbool(
            config.registry.settings.get(f"pyramid_sanity.{setting}", default)
        )
        if tween_enabled:
            config.add_tween(f"pyramid_sanity.tweens.{tween}", **options)
