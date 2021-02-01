import asyncio

from .engine.fanhuaji import FanhuajiEngine
from .engine.opencc import OpenCC as OpenCCEngine


class Converter():

    def __init__(self, engine, converter):
        self.engine = engine
        self.converter = converter

    def convert(self, content: str) -> str:
        """轉換 epub 內文

        Args:
            content (str): epub 內文字串

        Returns:
            [str]: 轉換後的內文
        """
        converted_content = None
        if not content:
            return None
        # opencc 轉換
        if self.engine == 'opencc':
            opencc = OpenCCEngine(self.converter)
            converted_content = opencc.convert(content)
        payload = {
            'text': content,
            'converter': self.converter
        }
        # 繁化姬同步轉換
        if self.engine == 'fanhuaji':
            fanhuaji = FanhuajiEngine()
            converted_content = fanhuaji.convert(**payload)
        # 繁化姬異步轉換
        if self.engine == 'fanhuaji_async':
            fanhuaji = FanhuajiEngine()
            converted_content = asyncio.get_event_loop().run_until_complete(
                fanhuaji.async_convert(**payload))
        return converted_content
