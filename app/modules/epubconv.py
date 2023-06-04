import logging
import os
import pathlib
import sys
import zipfile

from app.modules.convert import Convert
from app.modules.opf import OPF
from app.modules.renamer import ReNamer
from app.modules.zip import ZIP

logger = logging.getLogger('EpubConv')


class EPUBConv():
    def __init__(self, epub_abs_path: str) -> None:
        self.work_path = os.path.abspath(
            os.path.join(sys.argv[0], os.path.pardir))
        self.epub_abs_path = pathlib.Path(repr(epub_abs_path).strip("'"))

    def epub_extract(self) -> None:
        """解壓縮 epub 檔案"""
        ZIP.extract(self.epub_abs_path)

    @property
    def epub_file(self):
        """epub 檔案物件
        """
        zipfile = ZIP.zipfile(self.epub_abs_path)
        return EpubFile(zipfile, self.epub_abs_path)

    @property
    def epub_extract_path(self) -> str:
        """epub解壓縮的絕對路徑"""
        return f'{self.epub_abs_path}_files/'

    def opf_convert(self, opf_absolute_path: str) -> None:
        """OPF 檔案轉換

        Args:
            opf_absolute_path (str): OPF 檔案的絕對路徑
        """
        opf_file = OPF(opf_absolute_path+'.new')
        opf_file.language() # 語言標籤轉換

    def content_convert(self, content_absolute_path: str) -> None:
        """內容檔案轉換

        Args:
            content_absolute_path (str): 內容檔案的絕對路徑
        """
        logger.info('轉換檔案: ' + os.path.basename(content_absolute_path))
        with open(content_absolute_path, 'r', encoding='utf-8') as file:
            content = file.read()
        converted_content = Convert.convert(content)
        with open(content_absolute_path+'.new', 'w', encoding='utf-8') as file:
            file.write(converted_content)

    def file_rename(self, file_absolute_path: str) -> None:
        """檔案重新命名

        Args:
            file_absolute_path (str): 檔案的絕對路徑
        """
        ReNamer(file_absolute_path).rename()


class EpubFile():
    def __init__(self, zipfile: zipfile.ZipFile, epub_absolute_path: str) -> None:
        self.zipfile = zipfile
        self.epub_absolute_path = epub_absolute_path

    @property
    def content_files(self) -> list:
        """小說內容檔案的絕對路徑('ncx', 'opf', 'xhtml', 'html', 'htm', 'txt')
        """
        content_extensions = ['ncx', 'opf', 'xhtml', 'html', 'htm', 'txt']
        extract_path = f'{self.epub_absolute_path}_files/'
        content_files = []
        for file in self.zipfile.namelist():
            if file.endswith(tuple(content_extensions)):
                content_files.append(os.path.abspath(extract_path + file))
        return content_files

    @property
    def css_files(self) -> list:
        """所有 CSS 的絕對路徑
        """
        css_extensions = ['css']
        extract_path = f'{self.epub_absolute_path}_files/'
        css_files = []
        for file in self.zipfile.namelist():
            if file.endswith(tuple(css_extensions)):
                css_files.append(os.path.abspath(extract_path + file))
        return css_files

    @property
    def opf_file(self) -> str:
        """OPF 檔案的絕對路徑
        """
        opf_extensions = ['opf']
        extract_path = f'{self.epub_absolute_path}_files/'
        for file in self.zipfile.namelist():
            if file.endswith(tuple(opf_extensions)):
                return (os.path.abspath(extract_path + file))

    @property
    def epub_extract_path(self) -> str:
        """epub解壓縮的絕對路徑
        """
        return f'{self.epub_absolute_path}_files/'
