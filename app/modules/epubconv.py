import os
import pathlib
import sys
import zipfile

from app.modules.convert import Convert
from app.modules.opf import OPF
from app.modules.zip import ZIP


class EPUBConv():
    def __init__(self, epubAbsolutePath: str) -> None:
        self.workPath = os.path.abspath(
            os.path.join(sys.argv[0], os.path.pardir))
        self.epubAbsolutePath = pathlib.Path(repr(epubAbsolutePath).strip("'"))

    def epubDecompress(self) -> None:
        ZIP.decompress(self.epubAbsolutePath)

    def epubContents(self) -> list:
        contentExtension = ['ncx', 'opf', 'xhtml', 'html', 'htm', 'txt']
        zipfile = ZIP.zipfile(self.epubAbsolutePath)
        extractPath = f'{self.epubAbsolutePath}_files/'
        contentFiles = []
        for file in zipfile.namelist():
            if file.endswith(tuple(contentExtension)):
                contentFiles.append(os.path.abspath(extractPath + file))
        return contentFiles

    def opfConvert(self, opfAbsolutePath: str) -> None:
        opfFile = OPF(opfAbsolutePath+'.new')
        opfFile.language()

    def contentConvert(self, fileAbsolutePath: str) -> None:
        with open(fileAbsolutePath, 'r', encoding='utf-8') as file:
            content = file.read()
        convertedContent = Convert.convert(content)
        with open(fileAbsolutePath+'.new', 'w', encoding='utf-8') as file:
            file.write(convertedContent)
