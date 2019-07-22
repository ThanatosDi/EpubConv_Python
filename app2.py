import ctypes
import json
import mimetypes
import os
import re
import shutil
import sys
import time
import zipfile
from configparser import ConfigParser

from modules.console import Console
from modules.logger import Logger
from modules.opencc import OpenCC
from modules.utils.error import (ConfigError, FileTypeError, FileUnzipError,
                                 ZhConvertError)
from modules.utils.tools import encoding, get_key, resource_path
from modules.zhconvert import ZhConvert


class EPubConv:
    """ Electronic Publication Convert(EPubConv)
    """

    def __init__(self):
        """init

        Objects:
            logger -- log記錄檔物件
            workpath -- 本程式所在的絕對路徑
            cfg -- 讀取本程式路徑底下的 config.ini 設定檔內容
            convert_file_list -- 執行 unzip 方法後取得 EPub 中需要轉換的檔案之絕對路徑清單(list)
            new_filename -- 轉換後的 EPub 檔案的檔案名稱
        """
        self.workpath = os.path.abspath(
            os.path.join(sys.argv[0], os.path.pardir))
        self.logger = Logger(
            name='EPUB', workpath=self.workpath)
        self.cfg = self._read_config(f'{self.workpath}/config.ini')
        self.convert_file_list = None
        self.file_path = None

    def _read_config(self, config):
        """讀取設定檔

        Arguments:
            config {str} -- 設定檔路徑
        """
        if os.path.exists(config):
            self.logger.info('_read_config', 'read config')
            cfg = ConfigParser()
            cfg_encoding = encoding(config)['encoding']
            self.logger.info('_read_config encoding',encoding(config)['encoding'])
            cfg.read(config, encoding=cfg_encoding)
            self.logger.info(
                '_read_config', f"already read config\nengine: {cfg['setting']['engine']}\nconverter: {cfg['setting']['converter']}\nformat: {cfg['setting']['format']}")
            return cfg
        else:
            self.logger.info(f'_read_config', f'can\'t find "config.ini", please check config file.')

    """ def _read_allow_setting(self, config):
        '''讀取允許設定

        Arguments:
            config {str} -- allow_setting.json path
        '''
        print(resource_path('allow_setting.json')) """

    @property
    def _zip(self):
        """  """
        new_filename = self._filename
        lists = []
        for root, _dirs, files in os.walk(f'{self.file_path}_files/'):
            for filename in files:
                lists.append(os.path.join(root, filename))
        split_filename = os.path.splitext(new_filename)
        with zipfile.ZipFile(f'{split_filename[0]}_tc{split_filename[1]}', 'w', zipfile.zlib.DEFLATED) as z_f:
            for file in lists:
                arcname = file[len(f'{self.file_path}_files'):]
                z_f.write(file, arcname)

    def _unzip(self, file_path):
        """ 解壓縮 epub 檔案 """
        zip_file = zipfile.ZipFile(file_path)
        extract_path = file_path + '_files/'
        if os.path.isdir(extract_path):
            pass
        else:
            os.mkdir(extract_path)
        for names in zip_file.namelist():
            zip_file.extract(names, extract_path)
        self.convert_file_list = [os.path.abspath(extract_path + filename) for filename in zip_file.namelist() if any(
            filename.endswith(FileExtension) for FileExtension in ['ncx', 'opf', 'xhtml', 'html', 'htm', 'txt'])]
        if not self.convert_file_list:
            raise FileUnzipError(
                f'unzip "{os.path.basename(file_path)}" failed or epub file is None')
        zip_file.close()

    def convert(self, epub_file_path):
        """ epub 轉換作業

        Arguments:
            file {str} -- epub檔案的絕對位置(Absolute path)

        Raises:
            FileTypeError: 檔案格式不符例外處理
        """
        try:
            self.file_path = epub_file_path
            self.logger.info('convert', f'file path: {self.file_path}')
            self._check(epub_file_path)
            self._unzip(epub_file_path)
            if self.convert_file_list:
                self.logger.info(
                    'convert', f'unzip file "{epub_file_path}" success and get convert file list')
                self._convert_content(self.convert_file_list)
                self._rename(self.convert_file_list)
                self._zip
                self._clean
            self.logger.info('convert', f'success convert {os.path.basename(epub_file_path)}')
        except Exception as e:
            self.logger.error('convert', f'{str(e)}')

    def _rename(self, convert_file_list):
        """重新命名已轉換的檔案
        """
        for f in convert_file_list:
            self.logger.debug('rename', f'delete file "{os.path.basename(f)}"')
            os.remove(f)
            self.logger.debug('rename', f'rename "{os.path.basename(f)}"')
            os.rename(f'{f}.new', f)

    @property
    def _filename(self):
        """ 轉換 epub 檔案名稱非內文文檔 """
        converter_dict = {
            "s2t": ["s2t", "s2tw", "Traditional", "Taiwan", "WikiTraditional"],
            "t2s": ["t2s", "tw2s", "Simplified", "China", "WikiSimplified"]
        }
        converter = get_key(converter_dict, self.cfg['setting']['converter'])
        openCC = OpenCC(converter)
        new_filename = openCC.convert(os.path.basename(self.file_path))
        return os.path.join(os.path.dirname(self.file_path), new_filename)

    def _convert_content(self, convert_file_list):
        """內文文字轉換作業

        engine -- 轉換文字所使用的引擎
            [opencc, zhconvert]
        converter -- 該引擎所使用的模式
            opencc      : [s2t, t2s, s2tw, tw2s]
            zhconvert   : [Simplified, Traditional, China,
                Taiwan, WikiSimplified, WikiTraditional]

        Arguments:
            convert_file_list {list} -- 欲進行文字轉換的內文文檔的絕對路徑list
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
        if self.cfg['setting']['engine'] not in setting['engine']:
            raise ConfigError('Engine is not a right engine in "config.ini"')
        if self.cfg['setting']['converter'] not in setting['converter'][self.cfg['setting']['engine']]:
            raise ConfigError(
                'Converter is not a right converter in "config.ini"')
        if self.cfg['setting']['format'] not in setting['format']:
            raise ConfigError('Format is not a right format in "config.ini"')
        # 判斷轉換引擎並轉換
        if self.cfg['setting']['engine'].lower() == 'opencc':
            self.logger.debug('convert_text', 'engine: opencc')
            for f in convert_file_list:
                self.logger.debug(
                    'convert_text', f'now convert "{os.path.basename(f)}"')
                self._content_opt_lang(f)
                self._opencc(self.cfg['setting']['converter'], f)
        if self.cfg['setting']['engine'].lower() == 'zhconvert':
            self.logger.debug('convert_text', 'engine: zhconvert 繁化姬')
            for f in convert_file_list:
                self.logger.debug(
                    'convert_text', f'now convert "{os.path.basename(f)}"')
                self._content_opt_lang(f)
                self._zhconvert(self.cfg['setting']['converter'], f)

    def _opencc(self, converter, file):
        """opencc

        Arguments:
            converter {str} -- config.ini 中 converter 設定，轉換模式
            file {str} -- 欲進行文字轉換的內文文檔的絕對路徑
        """
        openCC = OpenCC(converter)
        f_encoding = encoding(file)['encoding']
        start_time = time.time()
        f_r = open(file, 'r', encoding=f_encoding).readlines()
        with open(file + '.new', 'w', encoding='utf-8') as f_w:
            for line in f_r:
                converted = openCC.convert(line)
                f_w.write(converted)
        end_time = time.time()
        self.logger.info('_opencc', f'convert file: {os.path.basename(file)} cost {"{:.2f}".format(end_time-start_time)}s')

    def _zhconvert(self, converter, file):
        """zhconvert 繁化姬
        
        Arguments:
            converter {str} -- config.ini 中 converter 設定，轉換模式
            file {str} -- 欲進行文字轉換的內文文檔的絕對路徑
        """
        zhconvert = ZhConvert()
        f_encoding = encoding(file)['encoding']
        start_time = time.time()
        with open(file, 'r', encoding=f_encoding) as f_r:
            zhconvert.convert(text=f_r.read(), converter=converter)
            with open(file + '.new', 'w', encoding='utf-8') as f_w:
                if zhconvert.text is None:
                    raise ZhConvertError()
                f_w.write(zhconvert.text)
        end_time = time.time()
        self.logger.info('_zhconvert', f'convert file: {os.path.basename(file)} cost {"{:.2f}".format(end_time-start_time)}s')

    def _content_opt_lang(self, content_file_path):
        """修改 content.opf 中語言標籤的值

        Arguments:
            content_file_path {str} -- 欲進行文字轉換的內文文檔的絕對路徑
        """
        converter = {
            "zh-TW": ["s2t", "s2tw", "Traditional", "Taiwan", "WikiTraditional"],
            "zh-CN": ["t2s", "tw2s", "Simplified", "China", "WikiSimplified"]
        }
        if os.path.basename(content_file_path) == 'content.opf':
            regex = re.compile(
                r"<dc:language>[\S]*</dc:language>", re.IGNORECASE)
            fileline = open(content_file_path, encoding='utf-8').read()
            if self.cfg['setting']['converter'] in converter["zh-TW"]:
                self.logger.info('_content_lang', 'convert language to zh-TW')
                modify = re.sub(
                    regex, f'<dc:language>zh-TW</dc:language>', fileline)
            if self.cfg['setting']['converter'] in converter["zh-CN"]:
                self.logger.info('_content_lang', 'convert language to zh-CN')
                modify = re.sub(
                    regex, f'<dc:language>zh-CN</dc:language>', fileline)
            open(content_file_path, 'w', encoding='utf-8').write(modify)

    # def _format(self, file_path):
    #     """  """
    #     modify_files = {}
    #     opf_tmp = []
    #     css_tmp = []
    #     content_tmp = []
    #     for root, _dirs, files in os.walk(f'{file_path}_files/'):
    #         for filename in files:
    #             if filename.endswith('opf'):
    #                 opf_tmp.append(filename)
    #             if filename.endswith('css'):
    #                 css_tmp.append(filename)
    #             if filename.endswith(('xhtml', 'html', 'htm')):
    #                 content_tmp.append(filename)
    #     modify_files['opf'] = opf_tmp
    #     modify_files['css'] = css_tmp
    #     modify_files['content'] = content_tmp
    #     #橫式
    #     if self.cfg['setting']['format'].lower() == 'horizontal':
    #         self.logger.info('_format', 'set content to horizontal')
    #         if not any(modify_files['css']):
    #             print('css file not found')
    #     #直式
    #     if self.cfg['setting']['format'].lower() == 'straight':
    #         self.logger.info('_format', 'set content to straight')
    #         print('直式')

    @property
    def _clean(self):
        """ 清除解壓縮後的檔案 """
        if os.path.isdir( f'{self.file_path}_files'):
            self.logger.info('_clean', f'delete tmp files: {self.file_path}_files')
            shutil.rmtree(f'{self.file_path}_files')
        else:
            self.logger.error('_clean', f'path: {self.file_path}_files not found.')

    def _check(self, file_path):
        """檢查檔案 MIME 格式

        Epub MIME : application/epub+zip

        Arguments:
            file_path {str} -- epub檔案的絕對位置(Absolute path)

        Raises:
            FileTypeError: 檔案格式不符例外處理
        """
        if not mimetypes.MimeTypes().guess_type(file_path)[0] == 'application/epub+zip':
            raise FileTypeError('File is not a epub file')


if __name__ == "__main__":
    EPubConvert = EPubConv()
    for epub in sys.argv[1:]:
        EPubConvert.convert(epub)
    os.system("pause")
    pass
