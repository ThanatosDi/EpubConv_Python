import os
import pathlib
import shutil
import sys
import zipfile

import chardet
from loguru import logger

from app.Modules.convert import Convert
from app.Modules.opf import OPF
from app.Modules.renamer import ReNamer
from app.Modules.zip import ZIP


class EPUBConv():
    def __init__(self, epub_abs_path: str) -> None:
        logger.info(f'正在處理 epub: {pathlib.Path(repr(epub_abs_path))}')
        self.work_path = os.path.abspath(
            os.path.join(sys.argv[0], os.path.pardir))
        self.epub_abs_path = pathlib.Path(repr(epub_abs_path).strip("'"))

    def epub_extract(self) -> None:
        """解壓縮 epub 檔案"""
        ZIP.extract(self.epub_abs_path)

    def epub_compress(self) -> None:
        """壓縮 epub 檔案"""
        ZIP.compress(self.epub_abs_path)

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
        opf_file.language()  # 語言標籤轉換

    def file_encoding(self, file):
        with open(file, 'rb') as file:
            detect = chardet.detect(file.read())
        logger.debug(detect)
        return detect['encoding']

    def content_convert(self, content_absolute_paths: list) -> None:
        """內容檔案轉換

        Args:
            content_absolute_paths (list): 內容檔案的絕對路徑
        """
        chapters = []
        for content_absolute_path in content_absolute_paths:
            encoding = self.file_encoding(content_absolute_path)
            with open(content_absolute_path, 'r', encoding=encoding) as file:
                content = file.read()
            chapter = {
                'path': content_absolute_path,
                'content': content
            }
            chapters.append(chapter)
        converted_chapters = Convert.convert(chapters)
        for chapter in converted_chapters:
            with open(chapter['path']+'.new', 'w', encoding='utf-8') as file:
                file.write(chapter['content'])

    def file_rename(self, files: list) -> None:
        """檔案重新命名

        Args:
            files (str): 檔案的絕對路徑清單
        """
        for file in files:
            ReNamer(file).rename()

    def clean(self) -> None:
        """ 清除解壓縮後的檔案 """
        if os.path.isdir(f'{self.epub_abs_path}_files'):
            logger.info(f'刪除暫存檔案: {self.epub_abs_path}_files')
            shutil.rmtree(f'{self.epub_abs_path}_files')
        else:
            logger.error(f'路徑: {self.epub_abs_path}_files 不存在，刪除失敗。')


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
