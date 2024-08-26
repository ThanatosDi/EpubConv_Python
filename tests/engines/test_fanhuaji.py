import asyncio

import aiohttp
import pytest

from app.Engines.fanhuaji import FanhuajiEngine
from app.Enums.EngineEnum import EngineEnum


class TestFanhuaji():
    @classmethod
    def setup_class(cls):
        cls.fanhuaji = FanhuajiEngine()
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    def test_fanhuaji_convert_s2t(self):
        params = {
            'chapters': [
                {'path': 'test_fanhuaji_convert_s2t.html',
                 'content': '使用 Python 撰写，epub 档案繁简横直互转'}
            ],
            'converter': 's2t'
        }
        ans = [{'content': '使用 Python 撰寫，epub 檔案繁簡橫直互轉',
                'path': 'test_fanhuaji_convert_s2t.html'}]
        text = self.fanhuaji.convert(**params)
        assert text == ans

    @pytest.mark.asyncio
    async def test_async_convert(self):
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy())
        params = {
            'chapters': [
                {'path': 'test_fanhuaji_convert_s2t_async.html',
                 'content': '使用 Python 撰写，epub 档案繁简横直互转'},
                {'path': 'test_fanhuaji_convert_s2t_async2.html',
                 'content': '并且使用异步处理'},
                {'path': 'test_fanhuaji_convert_s2t_async3.html',
                 'content': '非同期処理を使用する'}
            ],
            'converter': 's2t'
        }
        ans = [
            {'path': 'test_fanhuaji_convert_s2t_async.html',
                'content': '使用 Python 撰寫，epub 檔案繁簡橫直互轉'},
            {'path': 'test_fanhuaji_convert_s2t_async2.html', 'content': '並且使用異步處理'},
            {'path': 'test_fanhuaji_convert_s2t_async3.html', 'content': '非同期処理を使用する'}]
        result = await self.fanhuaji.async_convert(**params)
        assert result == ans
