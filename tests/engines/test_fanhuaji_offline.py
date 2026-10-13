"""繁化姬引擎的離線測試，以假的 HTTP 回應取代實際的 API 請求"""
from unittest.mock import MagicMock

import pytest

from app.engines import fanhuaji as fanhuaji_module
from app.engines.fanhuaji import (FanhuajiAPIError, FanhuajiEngine,
                                  FanhuajiInvalidKey, FanhuajiMissNecessaryKey)

API_ERROR = {'code': 1, 'data': [], 'msg': 'Invalid converter.'}


def api_success(text: str) -> dict:
    return {'code': 0, 'data': {'text': text}, 'msg': ''}


class FakeSyncResponse():
    def __init__(self, result: dict):
        self.status_code = 200
        self.result = result

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def raise_for_status(self):
        pass

    def json(self):
        return self.result


class FakeAsyncResponse():
    def __init__(self, result: dict):
        self.result = result

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def raise_for_status(self):
        pass

    async def json(self):
        return self.result


class FakeClientSession():
    def __init__(self, api: 'FakeApi'):
        self.api = api

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def post(self, url, data, headers):
        return FakeAsyncResponse(self.api.respond(data))


@pytest.fixture
def engine():
    return FanhuajiEngine()


class FakeApi():
    """記錄送出的請求，回應由 handler 決定（預設回傳 "[轉換器]原文"）"""

    def __init__(self):
        self.requests = []
        self.connector = MagicMock()
        self.handler = lambda data: api_success(f'[{data["converter"]}]{data["text"]}')

    def respond(self, data: dict) -> dict:
        self.requests.append(data)
        return self.handler(data)


@pytest.fixture
def sync_api(monkeypatch):
    """取代 requests.post"""
    api = FakeApi()
    monkeypatch.setattr(
        fanhuaji_module.requests, 'post',
        lambda url, data, headers: FakeSyncResponse(api.respond(data)))
    return api


@pytest.fixture
def async_api(monkeypatch):
    """取代 aiohttp.ClientSession 與 TCPConnector"""
    api = FakeApi()
    monkeypatch.setattr(fanhuaji_module.aiohttp, 'TCPConnector', api.connector)
    monkeypatch.setattr(
        fanhuaji_module.aiohttp, 'ClientSession', lambda connector: FakeClientSession(api))
    return api


class TestFanhuajiConvert():
    def test_chapters(self, engine, sync_api):
        chapters = [
            {'path': 'chapter1.html', 'content': '简体'},
            {'path': 'chapter2.html', 'content': '内存'},
        ]

        result = engine.convert(chapters=chapters, converter='s2twp')

        assert result == [
            {'path': 'chapter1.html', 'content': '[Taiwan]简体'},
            {'path': 'chapter2.html', 'content': '[Taiwan]内存'},
        ]
        assert [r['jpTextConversionStrategy'] for r in sync_api.requests] == ['protect', 'protect']

    def test_text(self, engine, sync_api):
        result = engine.convert(text='简体', converter='t2s')
        assert result == api_success('[Simplified]简体')
        assert sync_api.requests[0]['jpTextConversionStrategy'] == 'protect'

    @pytest.mark.parametrize('converter, expected', [
        ('s2t', 'Traditional'),
        ('s2tw', 'Traditional'),
        ('s2twp', 'Taiwan'),
        ('t2s', 'Simplified'),
        ('tw2s', 'Simplified'),
        ('tw2sp', 'China'),
        ('unknown', 'Traditional'),
    ])
    def test_converter_mapping(self, engine, sync_api, converter, expected):
        engine.convert(text='简体', converter=converter)
        assert sync_api.requests[0]['converter'] == expected

    def test_api_error(self, engine, sync_api):
        sync_api.handler = lambda data: API_ERROR
        with pytest.raises(FanhuajiAPIError, match='Invalid converter'):
            engine.convert(chapters=[{'path': 'a.html', 'content': '简体'}], converter='s2t')

    def test_invalid_key(self, engine):
        with pytest.raises(FanhuajiInvalidKey, match='foo'):
            engine.convert(text='简体', converter='s2t', foo='bar')

    def test_missing_converter(self, engine):
        with pytest.raises(FanhuajiMissNecessaryKey):
            engine.convert(text='简体')

    def test_missing_text_and_chapters(self, engine):
        with pytest.raises(FanhuajiMissNecessaryKey):
            engine.convert(converter='s2t')


@pytest.mark.asyncio
class TestFanhuajiAsyncConvert():
    async def test_chapters(self, engine, async_api):
        chapters = [
            {'path': 'chapter1.html', 'content': '简体'},
            {'path': 'chapter2.html', 'content': '内存'},
        ]

        result = await engine.async_convert(chapters=chapters, converter='s2twp')

        assert result == [
            {'path': 'chapter1.html', 'content': '[Taiwan]简体'},
            {'path': 'chapter2.html', 'content': '[Taiwan]内存'},
        ]
        assert [r['jpTextConversionStrategy'] for r in async_api.requests] == ['protect', 'protect']

    async def test_slice_long_content(self, engine, async_api):
        async_api.handler = lambda data: api_success(data['text'].upper())
        content = 'a' * 50_000 + 'b' * 50_000 + 'c' * 10

        result = await engine.async_convert(
            chapters=[{'path': 'chapter1.html', 'content': content}], converter='s2t')

        assert [len(r['text']) for r in async_api.requests] == [50_000, 50_000, 10]
        assert result[0]['content'] == content.upper()

    async def test_api_error(self, engine, async_api):
        async_api.handler = lambda data: API_ERROR
        with pytest.raises(FanhuajiAPIError, match='Invalid converter'):
            await engine.async_convert(
                chapters=[{'path': 'a.html', 'content': '简体'}], converter='s2t')

    async def test_invalid_key(self, engine):
        with pytest.raises(FanhuajiInvalidKey, match='foo'):
            await engine.async_convert(chapters=[], converter='s2t', foo='bar')

    @pytest.mark.parametrize('limit_per_host, expected', [(3, 3), (5, 5), (6, 5), (10, 5)])
    async def test_limit_per_host(self, engine, async_api, limit_per_host, expected):
        await engine.async_convert(
            chapters=[{'path': 'a.html', 'content': '简体'}], converter='s2t',
            aiohttp_tcp_limit=8, aiohttp_tcp_limit_per_host=limit_per_host)

        async_api.connector.assert_called_once_with(
            limit=8, limit_per_host=expected, force_close=True)
