import os
import subprocess
import sys

import pytest

from epubconv.config import (AppConfig, AppConfigError, Config, _parse_bool,
                             load_config)


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


INI = '''[ConvertSetting]
# 轉換相關設定
ENGINE=fanhuaji
converter=s2twp
format=vertical

[OtherSetting]
add_suffix=false
'''


class TestLoadConfig():
    def write_ini(self, tmp_path, content=INI):
        path = tmp_path / 'config.ini'
        path.write_text(content, encoding='utf-8')
        return path

    def test_read_file_ignoring_sections_and_case(self, tmp_path, restore_config):
        config = load_config(self.write_ini(tmp_path), env={})

        assert config is Config
        assert Config.ENGINE == 'fanhuaji'
        assert Config.CONVERTER == 's2twp'
        assert Config.FORMAT == 'vertical'
        assert Config.ADD_SUFFIX is False

    def test_env_overrides_file(self, tmp_path, restore_config):
        load_config(self.write_ini(tmp_path), env={'CONVERTER': 't2s', 'format': 'horizontal'})

        assert Config.ENGINE == 'fanhuaji'
        assert Config.CONVERTER == 't2s'
        assert Config.FORMAT == 'horizontal'

    def test_missing_file_uses_defaults(self, tmp_path, restore_config):
        load_config(tmp_path / 'missing.ini', env={})

        assert vars(Config) == vars(AppConfig({}))

    def test_reload_resets_unset_fields(self, tmp_path, restore_config):
        load_config(self.write_ini(tmp_path), env={})
        load_config(self.write_ini(tmp_path, 'converter=t2s\n'), env={})

        assert Config.ENGINE == 'opencc'
        assert Config.CONVERTER == 't2s'
        assert Config.ADD_SUFFIX is True

    def test_invalid_value_keeps_config(self, tmp_path, restore_config):
        load_config(self.write_ini(tmp_path), env={})
        before = dict(vars(Config))

        with pytest.raises(AppConfigError, match='ASYNC_LIMIT'):
            load_config(self.write_ini(tmp_path, 'engine=opencc\nasync_limit=abc\n'), env={})

        assert vars(Config) == before


def test_import_has_no_side_effects(tmp_path):
    """import epubconv 不可改變工作目錄（python -c 啟動時 sys.argv[0] 為 '-c'）"""
    code = (
        'import os; cwd = os.getcwd(); import epubconv; '
        'assert os.getcwd() == cwd, os.getcwd(); print(epubconv.Config.ENGINE)'
    )
    process = subprocess.run(
        [sys.executable, '-c', code],
        cwd=tmp_path, env=os.environ | {'ENGINE': 'fanhuaji'},
        capture_output=True, encoding='utf-8', timeout=60,
    )

    assert process.returncode == 0, process.stderr
    # import 時不讀環境變數與設定檔，只使用預設值
    assert process.stdout.strip() == 'opencc'
