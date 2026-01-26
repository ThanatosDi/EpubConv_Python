import opencc
from loguru import logger

from app.engines.engineABC import Engine
from app.Enums.ConverterEnum import ConverterEnum


class OpenCCEngine(Engine):

    def convert(self, converter: str, chapters: list = None, **kwargs) -> list[dict[str, str]]:
        """
        將給定的章節列表使用指定的 OpenCC 轉換器進行轉換。

        Args:
            converter (str): OpenCC 轉換器的名稱。
            chapters (list): 要進行轉換的章節列表，預設為 None。
            **kwargs: 其他參數。

        Returns:
            list[dict[str, str]]: 轉換後的章節列表。

        Raises:
            ValueError: 如果指定的轉換器不受支援。
        """
        if not ConverterEnum.opencc.value.has_value(converter):
            logger.error(f'{converter} 並非支援的 OpenCC 轉換器')
            raise ValueError(
                f'converter "{converter}" is not in OpenccConverter')
        converter: opencc.OpenCC = opencc.OpenCC(converter)
        for index, chapter in enumerate(chapters):
            chapters[index]['content'] = converter.convert(chapter['content'])
        return chapters

    def filename_convert(self, converter: str, filename: str) -> str:
        """
        將檔案名稱進行 OpenCC 轉換

        Parameters:
            converter (str): OpenCC 轉換器的名稱。
            filename (str): 需要轉換的檔案名稱。

        Returns:
            str: 轉換後的檔案名稱。
        """
        if not ConverterEnum.opencc.value.has_value(converter):
            logger.error(f'{converter} 並非支援的 OpenCC 轉換器')
            raise ValueError(
                f'converter "{converter}" is not in OpenccConverter')
        converter: opencc.OpenCC = opencc.OpenCC(converter)
        return converter.convert(filename)
