import logging
import os
import zipfile as zf

from app.engines.opencc import OpenCCEngine
from app.modules import config

logger = logging.getLogger('Zip')
opencc = OpenCCEngine()


class ZIP():
    def __init__(self):
        ...

    @staticmethod
    def compress(epubAbsolutePath: str) -> None:
        """將轉換後的資料夾內容壓縮回 epub

        Args:
            filename (str): 原始檔案的絕對路徑名稱
        """
        dirname = os.path.dirname(epubAbsolutePath)
        file_list = []
        for root, _dirs, files in os.walk(f'{epubAbsolutePath}_files/'):
            for name in files:
                file_list.append(os.path.join(root, name))
        new_filename = ZIP.convert_filename(epubAbsolutePath)
        saveAs = os.path.join(dirname, new_filename)
        with zf.ZipFile(saveAs, 'w', zf.zlib.DEFLATED) as z_f:
            for file in file_list:
                arcname = file[len(f'{epubAbsolutePath}_files'):]
                z_f.write(file, arcname)

    @staticmethod
    def decompress(epubAbsolutePath: str) -> None:
        """將 epub 解壓縮到資料夾中

        Args:
            epubAbsolutePath (str): 檔案的絕對路徑名稱
        """
        zipfile = zf.ZipFile(epubAbsolutePath)
        PATH = f'{epubAbsolutePath}_files/'
        if os.path.isdir(PATH):
            pass
        else:
            os.mkdir(PATH)
        for names in zipfile.namelist():
            zipfile.extract(names, PATH)

    def zipfile(epubAbsolutePath: str) -> zf.ZipFile:
        """取得 epub 的 zipfile 物件

        Args:
            epubAbsolutePath (str): 檔案的絕對路徑名稱

        Returns:
            zf.ZipFile: zipfile 物件
        """
        return zf.ZipFile(epubAbsolutePath)

    @staticmethod
    def convert_filename(epubAbsolutePath: str) -> str:
        MAPPING = {
            'tw2s': 't2s',
            's2tw': 's2t',
            's2twp': 's2t',
            'tw2sp': 't2s',
        }
        converter = config.CONVERTER
        # 僅取得檔案名稱不含路徑
        filename_with_extension = os.path.basename(epubAbsolutePath)
        converter = MAPPING.get(converter, converter)
        new_filename = opencc.convert(converter, filename_with_extension)
        return new_filename
