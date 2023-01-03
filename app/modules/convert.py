import asyncio

from app.engines.fanhuaji import FanhuajiEngine
from app.engines.opencc import OpenCCEngine
from app.Enums.EngineEnum import EngineEnum
from config import config

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
        if config.ENGINE == EngineEnum.opencc.value:
            return opencc.convert(**params)
        if config.ENGINE == EngineEnum.fanhuaji.value:
            return fanhuaji.convert(**params)
        if config.ENGINE == EngineEnum.fanhuaji_async.value:
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())
            return asyncio.run(fanhuaji.async_convert(**params))
