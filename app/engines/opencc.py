import opencc
from app.engines.engineABC import Engine
from app.Enums.ConverterEnum import ConverterEnum


class OpenCCEngine(Engine):
    def __init__(self,):
        ...

    def convert(self, converter: str, text: str, **kwargs) -> str:
        if not ConverterEnum.opencc.value.has_value(converter):
            raise ValueError(
                f'converter "{converter}" is not in OpenccConverter')
        converter: opencc.OpenCC = opencc.OpenCC(converter)
        return converter.convert(text)
