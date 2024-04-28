import asyncio

from app.Engines.fanhuaji import FanhuajiEngine
from app.Engines.opencc import OpenCCEngine
from app.Enums.EngineEnum import EngineEnum
from config.config import Config

opencc = OpenCCEngine()
fanhuaji = FanhuajiEngine()


class Convert():

    @staticmethod
    def convert(chapters: list) -> list[dict[str, str]]:
        """
        將給定的章節列表使用指定的轉換器進行轉換。

        Args:
            chapters (list): 要進行轉換的章節列表。

        Return:
            list[dict[str, str]]: 轉換後的章節列表。
            >>> [
            >>>    {"path": "章節路徑", "content": "章節內容"},
            >>>    {"path": "章節路徑", "content": "章節內容"},
            >>> ]

        Raises:
            ValueError: 如果配置中指定的轉換器不受支持。

        注意:
            - 要使用的轉換器由 `Config.CONVERTER` 的值確定。
            - 要使用的引擎由 `Config.ENGINE` 的值確定。
            - 如果引擎是 `opencc`，則調用 `opencc.convert` 方法。
            - 如果引擎是 `fanhuaji`，則調用 `fanhuaji.convert` 方法。
            - 如果引擎是 `fanhuaji_async`，則使用 asyncio 調用 `fanhuaji.async_convert` 方法。
            - 如果不支持該引擎，則會引發 `ValueError`。
        """
        params = {
            'converter': Config.CONVERTER,
            'chapters': chapters,
        }
        if Config.ENGINE == EngineEnum.opencc.value:
            return opencc.convert(**params)
        if Config.ENGINE == EngineEnum.fanhuaji.value:
            return fanhuaji.convert(**params)
        if Config.ENGINE == EngineEnum.fanhuaji_async.value:
            asyncio.set_event_loop_policy(
                asyncio.WindowsSelectorEventLoopPolicy())
            return asyncio.run(fanhuaji.async_convert(**params))
