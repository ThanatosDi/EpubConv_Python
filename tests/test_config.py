import pytest

from config.config import AppConfig, AppConfigError, _parse_bool


class TestParseBool():
    @pytest.mark.parametrize('value', ['true', 'True', 'TRUE', 'yes', '1', True])
    def test_truthy(self, value):
        assert _parse_bool(value) is True

    @pytest.mark.parametrize('value', ['false', 'no', '0', '', 'abc', False])
    def test_falsy(self, value):
        assert _parse_bool(value) is False


class TestAppConfig():
    def test_default_values(self):
        config = AppConfig({})
        assert config.ENGINE == 'opencc'
        assert config.CONVERTER == 's2t'
        assert config.FORMAT == 'horizontal'
        assert config.ASYNC_LIMIT == 5
        assert config.ASYNC_LIMIT_PER_HOST == 10
        assert config.FILE_CHECK is False
        assert config.ENABLE_PAUSE is False
        assert config.ADD_SUFFIX is True

    def test_read_from_env(self):
        config = AppConfig({
            'ENGINE': 'fanhuaji_async',
            'CONVERTER': 's2twp',
            'FORMAT': 'vertical',
        })
        assert config.ENGINE == 'fanhuaji_async'
        assert config.CONVERTER == 's2twp'
        assert config.FORMAT == 'vertical'

    def test_cast_int(self):
        config = AppConfig({'ASYNC_LIMIT': '3', 'ASYNC_LIMIT_PER_HOST': '4'})
        assert config.ASYNC_LIMIT == 3
        assert config.ASYNC_LIMIT_PER_HOST == 4

    def test_cast_bool(self):
        config = AppConfig({'FILE_CHECK': 'true', 'ENABLE_PAUSE': 'yes', 'ADD_SUFFIX': 'false'})
        assert config.FILE_CHECK is True
        assert config.ENABLE_PAUSE is True
        assert config.ADD_SUFFIX is False

    def test_invalid_int_raises(self):
        with pytest.raises(AppConfigError, match='ASYNC_LIMIT'):
            AppConfig({'ASYNC_LIMIT': 'abc'})

    def test_required_field_missing_raises(self):
        class RequiredConfig(AppConfig):
            REQUIRED: str

        with pytest.raises(AppConfigError, match='REQUIRED'):
            RequiredConfig({})

    def test_lowercase_field_is_ignored(self):
        class LowercaseConfig(AppConfig):
            lowercase: str = 'default'

        config = LowercaseConfig({'lowercase': 'changed'})
        assert config.lowercase == 'default'
