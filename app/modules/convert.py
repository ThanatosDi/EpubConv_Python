import asyncio

from app.engines.fanhuaji import FanhuajiEngine
from app.engines.opencc import OpenCCEngine

from app.modules import config

opencc = OpenCCEngine()
fanhuaji = FanhuajiEngine()


class Convert():
    def __init__(self): ...

    @staticmethod
    def convert(content: str) -> str:
        params = {
            'converter': config.CONVERTER,
            'text': content,
        }
        if config.ENGINE == 'opencc':
            return opencc.convert(**params)
        if config.ENGINE == 'fanhuaji':
            return fanhuaji.convert(**params)
        if config.ENGINE == 'fanhuaji_async':
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())
            return asyncio.run(fanhuaji.async_convert(**params))
