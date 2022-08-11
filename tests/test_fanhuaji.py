import asyncio
from engines.fanhuaji import FanhuajiEngine


class TestFanhuaji():
    @classmethod
    def setup_class(cls):
        cls.fanhuaji = FanhuajiEngine()
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    def test_fanhuaji_convert_s2t(self):
        params = {
            'text': '使用 Python 撰写，epub 档案繁简横直互转',
            'converter': 'Traditional'
        }
        text = self.fanhuaji.convert(**params)
        assert text == '使用 Python 撰寫，epub 檔案繁簡橫直互轉'

    def test_fanhuaji_convert_s2t_async(self):
        params = {
            'text': '使用 Python 撰写，epub 档案繁简横直互转',
            'converter': 'Traditional'
        }
        text = asyncio.run(
            self.fanhuaji.async_convert(**params)
        )
        assert text == '使用 Python 撰寫，epub 檔案繁簡橫直互轉'
