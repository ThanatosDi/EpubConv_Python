import opencc
from engines.engineABC import Engine


class OpenCCEngine(Engine):
    def __init__(self,):
        ...

    def convert(self, converter: str, text: str, **kwargs) -> str:
        converter: opencc.OpenCC = opencc.OpenCC(converter)
        return converter.convert(text)
