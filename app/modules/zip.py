import logging
import os
import zipfile as zf

from loguru import logger

from app.Engines.opencc import OpenCCEngine
from app.Enums.ConverterEnum import ConverterEnum, FilenameConverter
from config.config import Config

opencc = OpenCCEngine()


class ZIP():
    def __init__(self):
        ...

    @staticmethod
    def compress(epub_absolute_path: str) -> None:
        """將轉換後的資料夾內容壓縮回 epub

        Args:
            filename (str): 原始檔案的絕對路徑名稱
        """
        dirname = os.path.dirname(epub_absolute_path)
        file_list = []
        for root, _dirs, files in os.walk(f'{epub_absolute_path}_files/'):
            for name in files:
                file_list.append(os.path.join(root, name))
        new_filename = ZIP.convert_filename(epub_absolute_path)
        save_as = os.path.join(dirname, new_filename)
        with zf.ZipFile(save_as, 'w', zf.zlib.DEFLATED) as z_f:
            for file in file_list:
                logger.debug(file)
                arc_name = file[len(f'{epub_absolute_path}_files'):]
                z_f.write(file, arc_name)

    @staticmethod
    def extract(epub_absolute_path: str) -> None:
        """將 epub 解壓縮到資料夾中

        Args:
            epub_absolute_path (str): 檔案的絕對路徑名稱
        """
        zipfile = zf.ZipFile(epub_absolute_path)
        PATH = f'{epub_absolute_path}_files/'
        if os.path.isdir(PATH):
            pass
        else:
            os.mkdir(PATH)
        for names in zipfile.namelist():
            zipfile.extract(names, PATH)

    @staticmethod
    def zipfile(epub_absolute_path: str) -> zf.ZipFile:
        """取得 epub 的 zipfile 物件

        Args:
            epub_absolute_path (str): 檔案的絕對路徑名稱

        Returns:
            zf.ZipFile: zipfile 物件
        """
        return zf.ZipFile(epub_absolute_path)

    @staticmethod
    def convert_filename(epub_absolute_path: str) -> str:
        """轉換 epub 檔案名稱

        Args:
            epub_absolute_path (str): 檔案的絕對路徑名稱

        Returns:
            str: 轉換後的檔案名稱
        """
        converter: FilenameConverter = getattr(ConverterEnum.filename.value,
                                               Config.CONVERTER, None)
        if converter is None:
            converter = 's2t'
        # 僅取得檔案名稱不含路徑
        filename_with_extension = os.path.basename(epub_absolute_path)
        new_filename = opencc.filename_convert(
            converter.value, filename_with_extension)
        return new_filename
