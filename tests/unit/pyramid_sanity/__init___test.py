from unittest.mock import call, patch

import pytest
from pyramid.config import Configurator
from pyramid.tweens import MAIN

from pyramid_sanity import includeme


class TestIncludeMe:
    def test_it_puts_the_settings_into_the_registry(
        self, pyramid_config, SanitySettings, settings
    ):
        includeme(config=pyramid_config)

        SanitySettings.from_pyramid_settings.assert_called_once_with(
            pyramid_config.registry.settings
        )

        assert pyramid_config.registry.settings["pyramid_sanity"] == settings

    @pytest.mark.parametrize(
        "ingress_required,egress_required",
        [(True, True), (False, True), (True, False), (False, False),],
    )
    def test_it_adds_the_tweens(
        self, ingress_required, egress_required, pyramid_config, settings
    ):
        settings.ingress_required = ingress_required
        settings.egress_required = egress_required

        includeme(config=pyramid_config)

        ingress_tween_added = (
            call("pyramid_sanity.IngressTweenFactory")
            in pyramid_config.add_tween.call_args_list
        )
        assert ingress_tween_added == ingress_required

        egress_tween_added = (
            call("pyramid_sanity.EgressTweenFactory", over=MAIN)
            in pyramid_config.add_tween.call_args_list
        )
        assert egress_tween_added == egress_required

    @pytest.fixture
    def pyramid_config(self):
        with Configurator() as config:
            with patch.object(config, "add_tween", auto_spec=True):
                yield config


@pytest.fixture(autouse=True)
def SanitySettings(patch):
    return patch("pyramid_sanity.SanitySettings")


@pytest.fixture
def settings(SanitySettings):
    return SanitySettings.from_pyramid_settings.return_value
