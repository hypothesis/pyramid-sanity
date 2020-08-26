from unittest.mock import call, patch

import pytest
from pyramid.config import Configurator
from pyramid.tweens import MAIN

from pyramid_sanity import includeme


class TestIncludeMe:
    @pytest.mark.parametrize(
        "check_form,check_params,check_path,ascii_safe_redirects",
        [
            (True, True, True, True),
            (True, False, False, False),
            (False, True, False, False),
            (False, False, True, False),
            (False, False, False, True),
            (False, False, False, False),
        ],
    )
    def test_it_adds_the_invalid_form_tween_factory(  # pylint:disable=too-many-arguments
        self,
        check_form,
        check_params,
        check_path,
        ascii_safe_redirects,
        pyramid_config,
        settings,
    ):
        settings.check_form = check_form
        settings.check_params = check_params
        settings.check_path = check_path
        settings.ascii_safe_redirects = ascii_safe_redirects

        includeme(pyramid_config)

        assert (
            call("pyramid_sanity.tweens.invalid_form_tween_factory")
            in pyramid_config.add_tween.call_args_list
        ) == check_form

        assert (
            call("pyramid_sanity.tweens.invalid_query_string_tween_factory")
            in pyramid_config.add_tween.call_args_list
        ) == check_params

        assert (
            call("pyramid_sanity.tweens.invalid_path_info_tween_factory")
            in pyramid_config.add_tween.call_args_list
        ) == check_path

        assert (
            call("pyramid_sanity.tweens.ascii_safe_redirects_tween_factory", over=MAIN)
            in pyramid_config.add_tween.call_args_list
        ) == ascii_safe_redirects

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
