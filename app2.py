import ctypes
import json
import mimetypes
import os
import re
import sys
import zipfile

from modules.console import Console
from modules.utils.error import FileTypeError, FileUnzipError, ConfigError
from modules.logger import Logger
from modules.opencc import OpenCC
from modules.utils.tools import get_key


class EPUB:
    """ EPUB
    """

    def __init__(self):
        """
        """
        self.logger = Logger(name='EPUB')
        self.workpath = os.path.abspath(
            os.path.join(sys.argv[0], os.path.pardir))
        self.config = None
        self.convert_list = None
        self._read_config(f'{self.workpath}/config.json')

    def _read_config(self, config):
        """讀取設定檔

        Arguments:
            config {str} -- 設定檔路徑
        """
        if os.path.exists(config):
            self.logger.info('_read_config', 'read config')
            with open(config, 'r', encoding='utf-8') as r_c:
                self.config = json.loads(r_c.read())
            self.logger.info(
                '_read_config', f"Aleady read config\nengine: {self.config['engine']}\nconverter: {self.config['converter']}\nformat: {self.config['format']}")
            return self.config
        else:
            print('error')

    def zip(self):
        """  """

    def unzip(self, file_path):
        """ 解壓縮 epub 檔案 """
        zip_file = zipfile.ZipFile(file_path)
        extract_path = file_path + '_files/'
        if os.path.isdir(extract_path):
            pass
        else:
            os.mkdir(extract_path)
        for names in zip_file.namelist():
            zip_file.extract(names, extract_path)
        self.convert_list = [os.path.abspath(extract_path + filename) for filename in zip_file.namelist() if any(
            filename.endswith(FileExtension) for FileExtension in ['ncx', 'opf', 'xhtml', 'html', 'htm', 'txt'])]
        if not self.convert_list:
            raise FileUnzipError(
                f'unzip "{os.path.basename(file_path)}" failed or epub file is None')
        zip_file.close()

    def convert(self, file):
        """ epub 轉換作業

        Arguments:
            file {str} -- epub檔案的絕對位置(Absolute path)

        Raises:
            FileTypeError: 檔案格式不符例外處理
        """
        try:
            self._check(file)
            self.unzip(file)
            if self.convert_list:
                self.logger.info(
                    'convert', f'unzip file "{file}" success and get convert file list')
                self.convert_text(self.convert_list)
                self.rename(self.convert_list)
        except Exception as e:
            self.logger.error('convert', f'{str(e)}')
            os.system('pause')

    def rename(self, convert_list):
        """重新命名已轉換的檔案
        """
        for f in convert_list:
            self.logger.debug('rename', f'delete file "{os.path.basename(f)}"')
            os.remove(f)
            self.logger.debug('rename', f'rename "{os.path.basename(f)}"')
            os.rename(f'{f}.new', f)

    def _filename(self, file):
        """ 轉換 epub 檔案名稱非內文文檔 """
        converter_dict = {
            "s2t": ["s2t", "s2tw", "Traditional", "Taiwan", "WikiTraditional"],
            "t2s": ["t2s", "tw2s", "Simplified", "China", "WikiSimplified"]
        }
        converter = get_key(converter_dict, self.config['converter'])
        openCC = OpenCC(converter)
        newfilename = openCC.convert(os.path.basename(file))
        return os.path.join(os.path.dirname, newfilename)

    def convert_text(self, convert_list):
        """內文文字轉換作業

        engine -- 轉換文字所使用的引擎
            [opencc, zhconvert]
        converter -- 該引擎所使用的模式
            opencc      : [s2t, t2s, s2tw, tw2s]
            zhconvert   : [Simplified, Traditional, China,
                Taiwan, WikiSimplified, WikiTraditional]

        Arguments:
            convert_list {list} -- 欲進行文字轉換的內文文檔的絕對路徑list
        """
        setting = {
            "engine": ["opencc", "zhconvert"],
            "converter": {
                "opencc": ["s2t", "t2s", "s2tw", "tw2s"],
                "zhconvert": ["Simplified", "Traditional", "China", "Taiwan", "WikiSimplified", "WikiTraditional"]
            },
            "format": ["Straight", "Horizontal"]
        }
        # 檢查設定檔是否有無錯誤
        if self.config['engine'] not in setting['engine']:
            raise ConfigError('Engine is not a right engine in "config.json"')
        if self.config['converter'] not in setting['converter'][self.config['engine']]:
            raise ConfigError(
                'Converter is not a right converter in "config.json"')
        if self.config['format'] not in setting['format']:
            raise ConfigError('Format is not a right format in "config.json"')
        # 判斷轉換引擎並轉換
        if self.config['engine'].lower() == 'opencc':
            self.logger.debug('convert_text', 'engine: opencc')
            for f in convert_list:
                self.logger.debug(
                    'convert_text', f'now convert "{os.path.basename(f)}"')
                self._content_lang(f)
                self._opencc(self.config['converter'], f)
        if self.config['engine'].lower() == 'zhconvert':
            self.logger.debug('convert_text', 'engine: zhconvert 繁化姬')
            for f in convert_list:
                self._content_lang(f)

    def _opencc(self, converter, file):
        """opencc 轉換作業

        Arguments:
            converter {str} -- config.json 中 converter 設定，轉換模式
            file {str} -- 欲進行文字轉換的內文文檔的絕對路徑
        """
        openCC = OpenCC(converter)
        f_r = open(file, 'r', encoding='utf-8').readlines()
        with open(file + '.new', 'w', encoding='utf-8') as f_w:
            for line in f_r:
                converted = openCC.convert(line)
                f_w.write(converted)

    def _zhconvert(self, converter):
        """  """

    def _content_lang(self, file):
        """修改 content.opf 中語言標籤內容

        Arguments:
            file {str} -- 欲進行文字轉換的內文文檔的絕對路徑
        """
        converter = {
            "zh-TW": ["s2t", "s2tw", "Traditional", "Taiwan", "WikiTraditional"],
            "zh-CN": ["t2s", "tw2s", "Simplified", "China", "WikiSimplified"]
        }
        if os.path.basename(file) == 'content.opf':
            regex = re.compile(
                r"<dc:language>[\S]*</dc:language>", re.IGNORECASE)
            fileline = open(file, encoding='utf-8').read()
            if self.config['converter'] in converter["zh-TW"]:
                self.logger.info('_content_lang', 'convert language to zh-TW')
                modify = re.sub(
                    regex, f'<dc:language>zh-TW</dc:language>', fileline)
            if self.config['converter'] in converter["zh-CN"]:
                self.logger.info('_content_lang', 'convert language to zh-CN')
                modify = re.sub(
                    regex, f'<dc:language>zh-CN</dc:language>', fileline)
            open(file, 'w', encoding='utf-8').write(modify)

    def _format(self):
        """  """

    def _clean(self):
        """  """

    def _check(self, file):
        """檢查檔案 MIME 格式

        Epub MIME : application/epub+zip

        Arguments:
            file {str} -- epub檔案的絕對位置(Absolute path)

        Raises:
            FileTypeError: 檔案格式不符例外處理
        """
        if not mimetypes.MimeTypes().guess_type(file)[0] == 'application/epub+zip':
            raise FileTypeError('File is not a epub file')


if __name__ == "__main__":
    epub = EPUB()
    # epub.convert('1.epub')
    epub._filename('C:/Users/ThanatosDi/Desktop/Github/EpubConv_Python/1.epub')
    pass
