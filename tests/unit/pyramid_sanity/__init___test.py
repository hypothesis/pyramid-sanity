from unittest.mock import call

import pytest
from pyramid.tweens import MAIN

from pyramid_sanity import includeme


class TestIncludeMe:
    ALL_TWEEN_SETTINGS = (
        "pyramid_sanity.check_form",
        "pyramid_sanity.check_params",
        "pyramid_sanity.check_path",
        "pyramid_sanity.ascii_safe_redirects",
    )

    ALL_TWEEN_CALLS = (
        call("pyramid_sanity.tweens.invalid_form_tween_factory"),
        call("pyramid_sanity.tweens.invalid_query_string_tween_factory"),
        call("pyramid_sanity.tweens.invalid_path_info_tween_factory"),
        call("pyramid_sanity.tweens.ascii_safe_redirects_tween_factory", over=MAIN),
    )

    SETTINGS_AND_CALLS = tuple(zip(ALL_TWEEN_SETTINGS, ALL_TWEEN_CALLS))

    def test_all_tweens_are_enabled_by_default(self, pyramid_config):
        includeme(pyramid_config)

        assert pyramid_config.add_tween.call_args_list == list(self.ALL_TWEEN_CALLS)

    @pytest.mark.parametrize("setting,missing_call", SETTINGS_AND_CALLS)
    def test_individual_tweens_can_be_disabled(
        self, pyramid_config, setting, missing_call
    ):
        pyramid_config.registry.settings[setting] = False

        includeme(pyramid_config)

        expected_calls = list(self.ALL_TWEEN_CALLS)
        expected_calls.remove(missing_call)
        assert pyramid_config.add_tween.call_args_list == expected_calls

    def test_disable_removes_all_tweens(self, pyramid_config):
        pyramid_config.registry.settings["pyramid_sanity.disable_all"] = True

        includeme(pyramid_config)

        pyramid_config.add_tween.assert_not_called()

    @pytest.mark.parametrize("setting,expected_call", SETTINGS_AND_CALLS)
    def test_disabled_tweens_can_be_individually_enabled(
        self, pyramid_config, setting, expected_call
    ):
        pyramid_config.registry.settings["pyramid_sanity.disable_all"] = True
        pyramid_config.registry.settings[setting] = True

        includeme(pyramid_config)

        assert pyramid_config.add_tween.call_args_list == [expected_call]
