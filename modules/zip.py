import os
import zipfile as zf

from .env import Env
from .logger import Logger

env = Env()
logger = Logger('ZIP')


class ZIP():
    def __init__(self):
        pass

    def decompress(self, filename):
        """將 epub 解壓縮到資料夾中

        Args:
            filename (str): 檔案的絕對路徑名稱
        """
        zipfile = zf.ZipFile(filename)
        PATH = f'{filename}_files/'
        if os.path.isdir(PATH):
            pass
        else:
            os.mkdir(PATH)
        for names in zipfile.namelist():
            zipfile.extract(names, PATH)

    def compress(self, filename):
        """將轉換後的資料夾內容壓縮回 epub

        Args:
            filename (str): 原始檔案的絕對路徑名稱
        """
        file_list = []
        for root, _dirs, files in os.walk(f'{filename}_files/'):
            for name in files:
                file_list.append(os.path.join(root, name))
        new_filename = self.NewFilename(filename)
        with zf.ZipFile(new_filename, 'w', zf.zlib.DEFLATED) as z_f:
            for file in file_list:
                arcname = file[len(f'{filename}_files'):]
                z_f.write(file, arcname)

    def NewFilename(self, filename) -> str:
        """設定轉換後的語言標籤

        Args:
            filename (str): 原始檔案的絕對路徑名稱

        Returns:
            [str]: 轉換後的檔案名稱包含語言標籤
        """
        lang = 'None'
        if env.CONVERTER in ['s2t', 's2tw']:
            lang = 'tc'
        if env.CONVERTER in ['t2s', 'tw2s']:
            lang = 'sc'
        path = os.path.dirname(filename)
        split_filename = os.path.basename(filename).split('.')
        new_filename = os.path.join(
            path, f'{split_filename[0]}_{lang}.{split_filename[1]}')
        return new_filename
