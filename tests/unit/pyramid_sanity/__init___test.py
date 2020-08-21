from unittest.mock import patch

import pytest
from pyramid.config import PHASE3_CONFIG, Configurator
from pyramid.interfaces import ITweens

from pyramid_sanity import (
    EgressTweenFactory,
    IngressTweenFactory,
    _add_tween,
    includeme,
)


class TestIncludeMe:
    def test_it_registers_the_config_object(self, pyramid_config, SanitySettings):
        includeme(config=pyramid_config)

        SanitySettings.from_pyramid_settings.assert_called_once_with(
            pyramid_config.registry.settings
        )

        assert (
            pyramid_config.registry.settings["pyramid_sanity"]
            == SanitySettings.from_pyramid_settings.return_value
        )

    def test_it_registers_the_tween_factory(self, pyramid_config):
        # This test is kind of nonsense, just testing the code does what it
        # does.
        includeme(config=pyramid_config)

        pyramid_config.action.assert_called_once_with(
            ("tween", "pyramid_sanity.tween_factory", True),
            _add_tween,
            args=(pyramid_config,),
            order=PHASE3_CONFIG,
        )

    @pytest.fixture
    def SanitySettings(self, patch):
        return patch("pyramid_sanity.SanitySettings")

    @pytest.fixture
    def pyramid_config(self):
        with Configurator() as config:
            with patch.object(config, "action", auto_spec=True):
                yield config


class TestAddTween:
    # I'm going to level with you and say I'm not 100% what this is all up to
    # so these tests are very, what it does, and not very why

    def test_it_adds_the_ingress_tween(self, pyramid_config, tweens, sanity_settings):
        sanity_settings.check_form = True  # Any ingress would do here
        _add_tween(pyramid_config)

        assert tweens.explicit[0] == (
            "pyramid_sanity.ingress_tween_factory",
            IngressTweenFactory,
        )

    def test_it_doesnt_add_the_ingress_tween_if_not_required(
        self, pyramid_config, tweens
    ):
        _add_tween(pyramid_config)

        assert (
            "pyramid_sanity.ingress_tween_factory",
            IngressTweenFactory,
        ) not in tweens.explicit

    def test_it_adds_the_egress_tween_after_all_tweens(
        self, pyramid_config, tweens, sanity_settings
    ):
        sanity_settings.ascii_safe_redirects = True
        tweens.add_implicit(
            "fake_tween", lambda _handler, _registry: None
        )  # pragma: no cover
        implicit_tweens = tweens.implicit()
        assert not tweens.explicit

        _add_tween(pyramid_config)

        for pos, tween in enumerate(implicit_tweens):
            # All of the implicit tweens are now explicit
            assert tweens.explicit[pos] == tween

        # And at the end our EgressTweenFactory
        assert tweens.explicit[-1] == (
            "pyramid_sanity.egress_tween_factory",
            EgressTweenFactory,
        )

    def test_it_doesnt_add_the_egress_if_not_required(self, pyramid_config, tweens):
        implicit_tweens = tweens.implicit()
        assert not tweens.explicit

        _add_tween(pyramid_config)

        assert tweens.implicit() == implicit_tweens
        assert not tweens.explicit

    @pytest.fixture
    def tweens(self, pyramid_config):
        return pyramid_config.registry.queryUtility(ITweens)

    @pytest.fixture
    def pyramid_config(self, sanity_settings):
        with Configurator() as config:
            sanity_settings.all_off()
            config.registry.settings["pyramid_sanity"] = sanity_settings
            yield config
