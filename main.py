import os
import pathlib
import sys

from modules import config
from modules.convert import Convert
from modules.logger import Logger
from modules.opf import OPF
from modules.zip import ZIP

main = Logger(
    'EpubConv',
    config.LOGLEVEL,
    config.STDLEVEL,
)

zip = Logger(
    'Zip',
    config.LOGLEVEL,
    config.STDLEVEL,
)


class EPUBConv():
    def __init__(self):
        self.workPath = os.path.abspath(
            os.path.join(sys.argv[0], os.path.pardir))


    def EPUBConv(epubAbsolutePath: str) -> None:
        epubAbsolutePath = pathlib.Path(repr(epubAbsolutePath).strip("'"))
        ZIP.decompress(epubAbsolutePath)


if __name__ == '__main__':
    ...
