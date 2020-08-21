import pytest

from pyramid_sanity._settings import SanitySettings


class TestSanitySettings:
    def test_defaults(self, sanity_settings):
        self.assert_all_settings_equal(sanity_settings, True)

    def test_all_off(self, sanity_settings):
        sanity_settings.all_off()

        self.assert_all_settings_equal(sanity_settings, False)

    @pytest.mark.parametrize("truthy", (True, "True", "1"))
    def test_all_off_by_config(self, truthy):
        sanity_settings = SanitySettings.from_pyramid_settings(
            {"pyramid_sanity.disable_all": truthy}
        )

        self.assert_all_settings_equal(sanity_settings, False)

    @pytest.mark.parametrize("field", SanitySettings.BOOLEAN_FIELDS)
    @pytest.mark.parametrize(
        "value,expected",
        (
            (True, True),
            ("true", True),
            ("1", True),
            (False, False),
            ("false", False),
            ("0", False),
        ),
    )
    def test_from_pyramid_settings(self, field, value, expected):
        config = SanitySettings.from_pyramid_settings(
            {f"pyramid_sanity.{field}": value}
        )

        assert getattr(config, field) == expected

    @pytest.mark.parametrize("value,expected", ((True, True), (False, False)))
    def test_egress_required(self, sanity_settings, value, expected):
        sanity_settings.all_off()
        sanity_settings.ascii_safe_redirects = value

        assert sanity_settings.egress_required == expected

    @pytest.mark.parametrize(
        "field,expected",
        (
            ("check_form", True),
            ("check_params", True),
            ("check_path", True),
            ("irrelevant", False),
        ),
    )
    def test_ingress_required(self, sanity_settings, field, expected):
        sanity_settings.all_off()
        setattr(sanity_settings, field, True)

        assert sanity_settings.ingress_required == expected

    def assert_all_settings_equal(self, sanity_settings, value):
        assert sanity_settings.ascii_safe_redirects == value
        assert sanity_settings.check_form == value
        assert sanity_settings.check_params == value
        assert sanity_settings.check_path == value
