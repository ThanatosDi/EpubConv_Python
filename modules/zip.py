import os
import zipfile as zf

from .engine.opencc import OpenCC
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
        # 規格化環境變數
        converter = env.CONVERTER.replace('tw', 't')
        opencc = OpenCC(converter)
        # 建立文字標籤
        if converter == 't2s':
            lang = 'sc'
        if converter == 's2t':
            lang = 'tc'
        # 取得檔案資料夾絕對路徑
        path = os.path.dirname(filename)
        # 切割名稱為 [檔案名稱, 副檔名]
        split_filename = os.path.basename(filename).split('.')
        # 經過 opencc 轉換後的檔案名稱
        new_filename = opencc.convert(split_filename[0])
        # join 檔案資料夾絕對路徑、檔案名稱
        new_absfilename = os.path.join(
            path, f'{new_filename}_{lang}.{split_filename[1]}')
        return new_absfilename
