from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules import convert as convert_module
from app.modules.convert import Convert

CHAPTERS = [{'path': 'chapter1.xhtml', 'content': '简体'}]
RESULT = [{'path': 'chapter1.xhtml', 'content': '簡體'}]


@pytest.fixture
def engines(monkeypatch):
    opencc = MagicMock()
    opencc.convert.return_value = RESULT
    fanhuaji = MagicMock()
    fanhuaji.convert.return_value = RESULT
    fanhuaji.async_convert = AsyncMock(return_value=RESULT)
    monkeypatch.setattr(convert_module, 'opencc', opencc)
    monkeypatch.setattr(convert_module, 'fanhuaji', fanhuaji)
    return opencc, fanhuaji


class TestConvert():
    def test_opencc(self, engines, config):
        opencc, fanhuaji = engines
        config(engine='opencc', converter='s2twp')

        assert Convert.convert(CHAPTERS) == RESULT
        opencc.convert.assert_called_once_with(converter='s2twp', chapters=CHAPTERS)
        fanhuaji.convert.assert_not_called()

    def test_fanhuaji(self, engines, config):
        opencc, fanhuaji = engines
        config(engine='fanhuaji', converter='s2twp')

        assert Convert.convert(CHAPTERS) == RESULT
        fanhuaji.convert.assert_called_once_with(converter='s2twp', chapters=CHAPTERS)
        opencc.convert.assert_not_called()

    def test_fanhuaji_async(self, engines, config):
        _, fanhuaji = engines
        config(engine='fanhuaji_async', converter='s2twp',
               async_limit=3, async_limit_per_host=2)

        assert Convert.convert(CHAPTERS) == RESULT
        fanhuaji.async_convert.assert_awaited_once_with(
            converter='s2twp',
            chapters=CHAPTERS,
            aiohttp_tcp_limit=3,
            aiohttp_tcp_limit_per_host=2,
        )

    def test_unsupported_engine(self, engines, config):
        opencc, fanhuaji = engines
        config(engine='google')
        with pytest.raises(ValueError, match='google'):
            Convert.convert(CHAPTERS)
        opencc.convert.assert_not_called()
        fanhuaji.convert.assert_not_called()
