import opencc
from loguru import logger

from app.Engines.engineABC import Engine
from app.Enums.ConverterEnum import ConverterEnum


class OpenCCEngine(Engine):
    def __init__(self,):
        ...

    def convert(self, converter: str, chapters: list = None, **kwargs) -> list[dict[str, str]]:
        if not ConverterEnum.opencc.value.has_value(converter):
            logger.error(f'{converter} 並非支援的 OpenCC 轉換器')
            raise ValueError(
                f'converter "{converter}" is not in OpenccConverter')
        converter: opencc.OpenCC = opencc.OpenCC(converter)
        for index, chapter in enumerate(chapters):
            chapters[index]['content'] = converter.convert(chapter['content'])
        return chapters

    def filename_convert(self, converter: str, filename: str) -> str:
        if not ConverterEnum.opencc.value.has_value(converter):
            logger.error(f'{converter} 並非支援的 OpenCC 轉換器')
            raise ValueError(
                f'converter "{converter}" is not in OpenccConverter')
        converter: opencc.OpenCC = opencc.OpenCC(converter)
        return converter.convert(filename)
