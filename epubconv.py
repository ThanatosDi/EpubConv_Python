# -*- coding: utf8 -*-
import zipfile, os, glob, sys, shutil, chardet

##########################################################
# Author: Yichen Huang (Eugene)
# GitHub: https://github.com/yichen0831/opencc-python
# January, 2016
##########################################################

##########################################################
# Revised by: Hopkins1 
# June, 2016
# Apache License Version 2.0, January 2004
# - Use a tree-like structure hold the result during conversion
# - Always choose the longest matching string from left to right in dictionary
#   by trying lookups in the dictionary rather than looping
# - Split the incoming string into smaller strings before processing to improve speed
# - Only match once per dictionary
# - If a dictionary is configured as part of a group, only match once per group
#   in order of the listed dictionaries
# - Cache the results of reading a dictionary in self.dict_cache
# - Use "from __future__ import" to allow support for both Python 2.7
#   and Python >3.2
##########################################################

import io
import os
import json
import re
import sys

CONFIG_DIR = 'config'
DICT_DIR = 'dictionary'


class OpenCC:
    def __init__(self, conversion=None):
        """
        init OpenCC
        :param conversion: the conversion of usage, options are
         'hk2s', 's2hk', 's2t', 's2tw', 's2twp', 't2hk', 't2s', 't2tw', 'tw2s', and 'tw2sp'
         check the json file names in config directory
        :return: None
        """
        self.conversion_name = ''
        self.conversion = conversion
        self._dict_init_done = False
        self._dict_chain = list()
        self._dict_chain_data = list()
        self.dict_cache = dict()
        # List of sentence separators from OpenCC PhraseExtract.cpp. None of these separators are allowed as
        # part of a dictionary entry
        self.split_chars_re = re.compile(
            r'(\s+|-|,|\.|\?|!|\*|　|，|。|、|；|：|？|！|…|“|”|‘|’|『|』|「|」|﹁|﹂|—|－|（|）|《|》|〈|〉|～|．|／|＼|︒|︑|︔|︓|︿|﹀|︹|︺|︙|︐|［|﹇|］|﹈|︕|︖|︰|︳|︴|︽|︾|︵|︶|｛|︷|｝|︸|﹃|﹄|【|︻|】|︼)')
        if self.conversion is not None:
            self._init_dict()

    def convert(self, string):
        """
        Convert string from Simplified Chinese to Traditional Chinese or vice versa
        """
        if not self._dict_init_done:
            self._init_dict()
            self._dict_init_done = True

        result = []
        # Separate string using the list of separators in a regular expression
        split_string_list = self.split_chars_re.split(string)
        for i in range(0, len(split_string_list)):
            if i % 2 == 0:
                # Work with the text string
                # Append converted string to result
                result.append(self._convert(split_string_list[i], self._dict_chain_data))
            else:
                # Work with the separator
                # Append separator string to converted_string
                result.append(split_string_list[i])
        # Join it all together to return a result
        return "".join(result)

    def _convert(self, string, dictionary = [], is_dict_group = False):
        """
        Convert string from Simplified Chinese to Traditional Chinese or vice versa
        If a dictionary is part of a group of dictionaries, stop conversion on a word
        after the first match is found.
        :param string: the input string
        :param dictionary: list of dictionaries to be applied against the string
        :param is_dict_group: indicates if this is a group of dictionaries in which only
                              the first match in the dict group should be used
        :return: converted string
        """
        tree = StringTree(string)
        for c_dict in dictionary:
            if isinstance(c_dict, dict):
                tree.convert_tree(c_dict)
                if not is_dict_group:
                    # Don't reform the string here if the dictionary list is part of a group
                    # Recreate the tree for next loop iteration
                    tree = StringTree("".join(tree.inorder()))
            else:
                # This is a list of dictionaries. Call back in with the dictionary
                # list but specify that this is a group
                tree = StringTree(self._convert("".join(tree.inorder()), c_dict, True))
        return "".join(tree.inorder())

    def _init_dict(self):
        """
        initialize the dict with chosen conversion
        :return: None
        """
        if self.conversion is None:
            raise ValueError('conversion is not set')

        self._dict_chain = []
        config = self.conversion + '.json'
        config_file = os.path.join( WorkPath ,'opencc', CONFIG_DIR, config)
        with open(config_file) as f:
            setting_json = json.load(f)

        self.conversion_name = setting_json.get('name')

        for chain in setting_json.get('conversion_chain'):
            self._add_dict_chain(self._dict_chain, chain.get('dict'))

        self._dict_chain_data = []
        self._add_dictionaries(self._dict_chain, self._dict_chain_data)
        self._dict_init_done = True

    def _add_dictionaries(self, chain_list, chain_data):
        for item in chain_list:
            if isinstance(item, list):
                chain = []
                self._add_dictionaries(item, chain)
                chain_data.append(chain)
            else:
                if not item in self.dict_cache:
                    map_dict = {}
                    with io.open(item, "r", encoding="utf-8") as f:
                        for line in f:
                            key, value = line.strip().split('\t')
                            map_dict[key] = value
                    chain_data.append(map_dict)
                    self.dict_cache[item] = map_dict
                else:
                    chain_data.append(self.dict_cache[item])

    def _add_dict_chain(self, dict_chain, dict_dict):
        """
        add dict chain
        :param dict_chain: the dict chain to add to
        :param dict_dict: the dict to be added in
        :return: None
        """
        if dict_dict.get('type') == 'group':
            # Create a sublist of dictionaries for a group
            chain = []
            for dict_item in dict_dict.get('dicts'):
                self._add_dict_chain(chain, dict_item)
            dict_chain.append(chain)
        elif dict_dict.get('type') == 'txt':
            filename = dict_dict.get('file')
            dict_file = os.path.join( WorkPath ,'opencc', DICT_DIR, filename)
            dict_chain.append(dict_file)

    def set_conversion(self, conversion):
        """
        set conversion
        :param conversion: the conversion of usage, options are
         'hk2s', 's2hk', 's2t', 's2tw', 's2twp', 't2hk', 't2s', 't2tw', 'tw2s', and 'tw2sp'
         check the json file names in config directory
        :return: None
        """
        if self.conversion == conversion:
            return
        else:
            self._dict_init_done = False
            self.conversion = conversion

class StringTree:
    """
    Class to hold string during modification process.
    """
    def __init__(self, string):
        self.string = string
        self.left = None
        self.right = None
        self.string_len = len(string)
        self.matched = False

    def convert_tree(self, test_dict):
        """
        Compare smaller and smaller sub-strings going from left to
        right against test_dict. If an entry is found, place the remaining
        string portion on the left and right into sub-trees and recurively
        convert each.
        :param test_dict: the dict currently being applied againt
                        the string
        :return: None
        """
        if self.matched == True:
            if self.left is not None:
                self.left.convert_tree(test_dict)
            if self.right is not None:
                self.right.convert_tree(test_dict)
        else:
            test_len = self.string_len
            while test_len != 0:
                # Loop through trying successively smaller substrings in the dictionary
                for i in range(0, self.string_len - test_len + 1):
                    if self.string[i:i+test_len] in test_dict:
                        # Match found.
                        if i > 0:
                            # Put everything to the left of the match into the left sub-tree and further process it
                            self.left = StringTree(self.string[:i])
                            self.left.convert_tree(test_dict)
                        if (i+test_len) < self.string_len:
                            # Put everything to the left of the match into the left sub-tree and further process it
                            self.right = StringTree(self.string[i+test_len:])
                            self.right.convert_tree(test_dict)
                        # Save the dictionary value in this tree
                        value = test_dict[self.string[i:i+test_len]]
                        if len(value.split(' ')) > 1:
                            # multiple mapping, use the first one for now
                            value = value.split(' ')[0]
                        self.string = value
                        self.string_len = len(self.string)
                        self.matched = True
                        return
                test_len -= 1

    def inorder(self):
        """
        Inorder traversal of this tree
        :param None
        :return: list of words from a inorder traversal of the tree
        """
        result = []
        if self.left is not None:
            result += self.left.inorder()
        result.append(self.string)
        if self.right is not None:
            result += self.right.inorder()
        return result

###########################################
# Author: ThanatosDi
# GitHub: https://github.com/Kutinging
# 2018,07,18
###########################################

WorkPath = os.path.abspath(os.path.join(sys.argv[0],os.path.pardir)) #應用程式絕對路徑
EpubFilePath = sys.argv #epub檔案絕對路徑
OpenccPath = WorkPath + '\opencc' #opencc絕對路徑
OpenccConfig = {"s2t":['STPhrases.txt','STCharacters.txt'],"t2s":['TSPhrases.txt','TSCharacters.txt'],"s2tw":['STPhrases.txt','STCharacters.txt','TWVariants.txt'],"tw2s":['TSPhrases.txt','TWVariantsRevPhrases.txt','TWVariantsRev.txt','TSCharacters.txt']}
format_mode_list = ['Horizontal','Straight']

import time, json

class Config_LoadFailed(Exception):
    pass
class Check_OpenCCNotFound(Exception):
    pass
class Config_ModeErrror(Exception):
    pass
class Config_FormatErrror(Exception):
    pass
class Check_FileNotEPUB(Exception):
    pass
class ZIP_ZipFailed(Exception):
    pass
class ZIP_UnzipFailed(Exception):
    pass
class Convert_FormatFailed(Exception):
    pass
class Convert_ConvertFailed(Exception):
    pass
class Convert_RenameFailed(Exception):
    pass
class Convert_FilenameFailed(Exception):
    pass
class Convert_encodingFailed(Exception):
    pass
class Convert_CleanFailed(Exception):
    pass


class config:
    @staticmethod
    def load():
        """
        # 讀取設定檔
        """
        try:
            if not os.path.isfile(f'{WorkPath}\config.json'):
                raise Config_LoadFailed(f'>> config.load : 缺少設定檔')
            with open(f'{WorkPath}\config.json' , 'r',encoding='utf-8') as reader:
                config = json.loads(reader.read())
            if config['format'] not in format_mode_list:
                raise Config_FormatErrror(f'>> config.load : config.json 中 format 設定錯誤，請確定 Horizontal(橫) 或 Straight(直)')
            if config['mode'] not in OpenccConfig:
                raise Config_ModeErrror(f'>> config.load : config.json 中 mode 設定錯誤，(簡轉繁)s2t,(繁轉簡)t2s')
            return config
        except Config_FormatErrror as e:
            log.write(f'{str(e)}')
            print(f'{str(e)}')
            os.system("pause")
            sys.exit(0)
        except Config_ModeErrror as e:
            log.write(f'{str(e)}')
            print(f'{str(e)}')
            os.system("pause")
            sys.exit(0)
        except Config_LoadFailed as e:
            log.write(f'{str(e)}')
            print(f'{str(e)}')
            os.system("pause")
            sys.exit(0)
        except Exception as e:
            log.write(f'>> config.load : 讀取設定檔發生錯誤 -> {str(e)}')
            print(f'>> config.load : 讀取設定檔發生錯誤 -> {str(e)}')
            os.system("pause")
            sys.exit(0)

class Check:
    @staticmethod
    def OpenCC(mode):
        """
        # 執行 OpenCC 確認\n
        # Check.OpenCC(mode)
        """
        try:
            for file in OpenccConfig[mode]:
                if not os.path.isfile(f'{OpenccPath}\\dictionary\\{file}'):
                    raise Check_OpenCCNotFound(f'>> Check.OpenCC({mode}) : 缺少翻譯檔 {file}')
            if not os.path.isfile(f'{OpenccPath}\\config\\{mode}.json'):
                raise Check_OpenCCNotFound(f'>> Check.OpenCC({mode}) : 缺少設定檔 {mode}.json')
            return True
        except Check_OpenCCNotFound as e:
            log.write(str(e))
            print(str(e))
            return False
        except Exception as e:
            log.write(f'>> Check.OpenCC : 檢查 OpenCC 時發生錯誤 -> {str(e)}')
            print(f'>> Check.OpenCC : 檢查 OpenCC 時發生錯誤 -> {str(e)}')
            return False
    
    @staticmethod
    def File(Files):
        """
        # 執行檔案確認\n
        # Check.File(Files)
        """
        try:
            if not os.path.splitext(Files)[-1]=='.epub':
                raise Check_FileNotEPUB(f'>> Check.File : {(Files)} 該檔案非EPUB格式')
            return True
        except Check_FileNotEPUB as e:
            log.write(f'{str(e)}')
            print(f'{str(e)}')
            return False
        except Exception as e:
            log.write(f'>> Check.File : 發生無法處理問題 -> {str(e)}')
            print(f'>> Check.File : 發生無法處理問題 -> {str(e)}')
            return False
            

class ZIP:
    @staticmethod
    def zip(zippath,epubname):
        """
        # 建立壓縮檔\n
        # ZIP.zip(zippath,epubname)\n
        # zippath : 壓縮路徑\n
        # epubname : 檔案名稱\n
        """
        try:
            if os.path.isfile(epubname):
                pass
            else:
                FileList = []  
                if os.path.isfile(zippath):  
                    FileList.append(zippath)  
                else :  
                    for root, _dirs, files in os.walk(zippath):  
                        for name in files:  
                            FileList.append(os.path.join(root, name))  
                    
                zf = zipfile.ZipFile(epubname, 'w', zipfile.zlib.DEFLATED)  
                for tar in FileList:  
                    arcname = tar[len(zippath):]
                    zf.write(tar,arcname)  
                zf.close()
                if os.path.isfile(epubname):
                    Convert.clean(zippath)
                    return True
                else:
                    Convert.clean(zippath)
                    return False
        except Exception as e:
            log.write(f'>> ZIP.zip : 壓縮發生錯誤 -> {str(e)}')
            print(f'>> ZIP.zip : 壓縮發生錯誤 -> {str(e)}')
            return False
    
    @staticmethod
    def unzip(Epubfile):
        """ 
        # 將 epub 使用 zip 方式解壓縮，並取得epub中的書籍簡介、內文檔案絕對路徑\n
        # ZIP.unzip(Epubfile)
        """  
        try:
            zip_file = zipfile.ZipFile( Epubfile )  
            unzippath = Epubfile + '_files\\'
            if os.path.isdir( Epubfile + "_files"):  
                pass  
            else:  
                os.mkdir( Epubfile + "_files")  
            for names in zip_file.namelist():  
                zip_file.extract(names, Epubfile + "_files/")
            FileList = [os.path.abspath( unzippath + filename) for filename in zip_file.namelist() if any(filename.endswith(FileExtension) for FileExtension in ['ncx', 'opf', 'xhtml', 'html', 'htm', 'txt'])]
            zip_file.close()
            return FileList
        except Exception as e:
            log.write(f'>> ZIP.unzip : 解壓縮發生錯誤 -> {str(e)}')
            print(f'>> ZIP.unzip : 解壓縮發生錯誤 -> {str(e)}')
            return False


class Convert:
    @staticmethod
    def format(Epubfile,format_mode='Horizontal'):
        """
        # 將橫式轉換成直式\n
        # Convert.format(Epubfile,format_mode)\n
        # Epubfile : 檔案\n
        # format_mode : Straight(直式),Horizontal(橫式)
        """
        try:
            FileList = []
            CSSList = []
            CSSname = ''
            for dirPath, dirNames, fileNames in os.walk(f'{Epubfile}_files\\'):
                for file in fileNames:
                    if any(file.endswith(end) for end in ['opf', 'xhtml', 'html', 'htm','css']):
                        if not file.find('css')==-1:
                            CSSList.append(os.path.join(dirPath, file))
                        FileList.append(os.path.join(dirPath, file))
                        
            if format_mode == 'Straight':
                print(f'\n>>>> 讀取設定檔 : format-->直式(Straight)\n')
                #if not CSSList[0].find('css')==-1 and os.path.isfile(CSSList[0]):
                if any(CSSList): #判斷是否有 .css檔案
                    CSSname = CSSList[0]
                    #讀取 css 檔案，並抓取出 html{ 起始行
                    with open(CSSList[0],'r+',encoding='utf-8') as css:
                        linecount = 0
                        lineslist = []
                        start = None
                        for line in css:
                            lineslist.append(line)
                            linecount += 1
                            if re.findall(r'html(?:.*){',line):
                                start = linecount
                    lines = open(CSSList[0],'r+',encoding='utf-8').read()
                    #判斷是否有無直式css 如果沒有插入後建立檔案
                    if start is None:
                        print(f'>>>> 未發現 {os.path.basename(CSSname)} 中有html標籤\n------>新增直式CSS到 {os.path.basename(CSSname)} 中\n')
                        lineslist.insert(0,'html{\n\twriting-mode: vertical-rl;\n\t-webkit-writing-mode: vertical-rl;\n\t-epub-writing-mode: vertical-rl;\n}\n')
                        with open(CSSList[0],'w+',encoding='utf-8') as css:
                                css.writelines(lineslist)
                    else:
                        print(f'>>>> 發現 {os.path.basename(CSSname)} 中有html標籤\n------>新增直式CSS到 {os.path.basename(CSSname)} 中\n')
                        if not any(re.findall(r'.*writing-mode(?:\:|.*\:).*',lines)):
                            lineslist.insert(start,'\twriting-mode: vertical-rl;\n\t-webkit-writing-mode: vertical-rl;\n\t-epub-writing-mode: vertical-rl;\n')
                            with open(CSSList[0],'w+',encoding='utf-8') as css:
                                css.writelines(lineslist)
                else:
                    print(f'>>>> 未發現該 epub 中有 .css 檔')
                    if not os.path.isdir(f'{Epubfile}_files/OEBPS'):
                        os.mkdir(f'{Epubfile}_files/OEBPS')
                    if not os.path.isdir(f'{Epubfile}_files/OEBPS/Styles'):
                        os.mkdir(f'{Epubfile}_files/OEBPS/Styles')
                    with open(f'{Epubfile}_files/OEBPS/Styles/style.css', 'a', encoding='utf-8') as cssfile:
                        cssfile.write('html{\n\twriting-mode: vertical-rl;\n\t-webkit-writing-mode: vertical-rl;\n\t-epub-writing-mode: vertical-rl;\n}\n')
                    CSSname = 'style.css'

                for File in FileList:
                    print(f'>>>> 正在轉換 {os.path.basename(File)} 格式為直式')
                    if not File.find('content.opf')==-1:
                        modify = open(File,encoding='utf-8').read().replace('<spine toc="ncx">', '<spine toc="ncx" page-progression-direction="rtl">')
                        open(File,'w',encoding='utf-8').write(modify)
                    
                    
                    if any(File.find(end) for end in ['xhtml', 'html', 'htm']):
                        regex = re.compile(r".*<\/head>.*", re.IGNORECASE)
                        lines = open(File,encoding='utf-8').read()
                        if not any(re.findall(r'link href=\"[\S]*.css\"',lines)):
                            m = re.findall(regex,lines)
                            if os.path.dirname(CSSname)==os.path.dirname(File):
                                CSSpath = CSSname.replace(f'{Epubfile}_files','.')
                            else:
                                CSSpath = f'../Styles/{os.path.basename(CSSname)}'
                            modify = re.sub(regex,f'\t<link href="{(CSSpath)}" rel="stylesheet" type="text/css"/>\n</head>',lines)
                            open(File,'w',encoding='utf-8').write(modify)

            if format_mode == 'Horizontal':
                print(f'>> 讀取設定檔 : format-->橫式(Horizontal)')
                #if not CSSList[0].find('.css')==-1 and os.path.isfile(CSSList[0]):
                if any(CSSList): #判斷是否有 .css檔案
                    with open(CSSList[0],'r+',encoding='utf-8') as css:
                        linecount = 0
                        lineslist = []
                        start = None
                        for line in css:
                            lineslist.append(line)
                            linecount += 1
                            if re.findall(r'html(?:.*){',line):
                                start = linecount
                    lines = open(CSSList[0],'r+',encoding='utf-8').read()
                    if start is not None:
                        if any(re.findall(r'.*writing-mode(?:\:|.*\:).*',lines)):
                            print(f'>>>> 發現 {os.path.basename(CSSname)} 中有html標籤\n------>刪除直式CSS中\n')
                            open(CSSList[0],'w',encoding='utf-8').write(re.sub(r'.*writing-mode(?:\:|.*\:).*','',lines))
                else:
                    print(f'>>>> 未發現該 epub 中有 .css 檔')
                    pass
                for File in FileList:
                    print(f'>>>> 正在轉換 {os.path.basename(File)} 格式為橫式')
                    if not File.find('content.opf')==-1:
                        modify = open(File,encoding='utf-8').read().replace('<spine toc="ncx" page-progression-direction="rtl">','<spine toc="ncx">')
                        open(File,'w',encoding='utf-8').write(modify)
                
            return True
        except Exception as e:
            log.write(f'Convert.format : 格式轉換發生錯誤 -> {str(e)}')
            print(f'Convert.format : 格式轉換發生錯誤 -> {str(e)}')
            return False

    @staticmethod
    def convert(mode,FileList):
        """
        # 翻譯檔案\n
        # Convert.convert(mode,FileList)
        """
        openCC = OpenCC(mode)
        while True:
            try:
                for File in FileList:
                    if os.path.basename(File)=='content.opf':
                        regex = re.compile(r"<dc:language>[\S]*</dc:language>", re.IGNORECASE)
                        fileline = open(File,encoding='utf-8').read()
                        m = re.findall(regex,fileline)
                        if mode=='s2t' or mode=='s2tw':
                            modify = re.sub(regex,f'<dc:language>zh-TW</dc:language>',fileline)
                        if mode=='t2s' or mode=='tw2s':
                            modify = re.sub(regex,f'<dc:language>zh-CN</dc:language>',fileline)
                        open(File,'w',encoding='utf-8').write(modify)
                    with open(File,'r',encoding='utf-8') as FileRead:
                        FileLines = FileRead.readlines()
                    if os.path.isfile(File + '.new'):
                        pass
                    else:
                        with open( File + '.new','w',encoding='UTF-8') as FileWrite:
                            print(f'>>>> 正在翻譯 {os.path.basename(File)} 中')
                            for Line in FileLines:
                                converted = openCC.convert(Line)
                                FileWrite.write(converted)
                return True
                break
            except Exception as e:
                print(f'>> Convert.convert : 轉換發生錯誤 -> {str(e)}')
                log.write(f'>> Convert.convert : 轉換發生錯誤 -> {str(e)}')
                if not Convert.encoding(File)==False: #轉換編碼:將簡體中文編碼轉utf-8編碼
                    continue
                else:
                    break

    @staticmethod
    def Rename(FileList):
        """
        # 重新命名檔案\n
        # Convert.Rename(FileList)
        """
        try:
            for FileName in FileList:
                print(f'>>>> 重新命名 {os.path.basename(FileName)}.new 到 {os.path.basename(FileName)}')
                os.remove(FileName)
                os.rename(FileName+'.new',FileName)
            return True
        except Exception as e:
            log.write(f'>> Convert.Rename : {str(e)}')
            print(f'>> Convert.Rename : 重新命名 {FileName}.new 發生錯誤')
            return False

    @staticmethod
    def FileName(mode,FilePath):
        """
        # 翻譯檔案名稱\n
        # Convert.FileName(mode,FilePath)
        """
        openCC = OpenCC(mode)
        Path = os.path.dirname( FilePath )
        FileName = openCC.convert(os.path.basename( FilePath ))
        return os.path.join(Path,FileName)

    @staticmethod
    def encoding(File):
        """
        # 當檔案並非 UTF8格式時轉換成UTF8\n
        # Convert.encoding(File)
        """
        try:
            with open( File , 'rb') as f:
                encoding = (chardet.detect(f.read())['encoding']).upper()
                print( File +' encoding is '+ encoding)
                if encoding=='GB18030' or encoding=='GBK' or encoding=='GB2312':
                    encoding = 'GB18030'
                    print(f'>>>> 使用 {encoding} 開啟檔案')
                    with open( File , 'r', encoding=encoding) as FileRead:
                        FileLines = FileRead.readlines()
                        with open( File ,'w',encoding='UTF-8') as FileWrite:
                            print(f'>>>> 轉換 {File} 編碼從 {encoding} 到 UTF-8 ')
                            for Line in FileLines:
                                FileWrite.write(Line)
                elif encoding=='UTF-8':
                    print('檔案已經是 UTF-8 編碼\n跳過')
                    pass
            return encoding
        except Exception as e:
            log.write(f'>> Convert.encoding : {str(e)}')
            print(f'>> Convert.encoding : {os.path.basename(File)} 編碼轉換發生錯誤')
            return False

    @staticmethod
    def clean(DirPath):
        """
        # 刪除暫存檔\n
        # Convert.clean(DirPath)
        """
        try:
            if os.path.isdir( DirPath ):
                shutil.rmtree( DirPath )
        except Exception as e:
            log.write(f'>> Convert.clean : {str(e)}')
            print(f'>> Convert.clean : 刪除暫存檔發生錯誤')
            return False
class log:
    @staticmethod
    def _get_time():
        """
        # 取得系統當下時間
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 

    @staticmethod
    def write(message):
        """
        # log 資料寫入
        """
        with open( f'{WorkPath}/epubconv.log','a',encoding='UTF-8') as logfile:
            logfile.write(log._get_time()+' '+message+'\n')

def main():
    try:
        setting = config.load()
        if len(EpubFilePath) > 1:
            for index in range(len(EpubFilePath)-1):
                if Check.OpenCC(setting['mode']) and Check.File(EpubFilePath[index+1]):
                    FileList = ZIP.unzip(EpubFilePath[index+1])
                    if not FileList == None:
                        if Convert.convert(setting['mode'],FileList):
                            if Convert.Rename(FileList):
                                if Convert.format(EpubFilePath[index+1],format_mode=setting['format']):
                                    ZIP.zip(f'{EpubFilePath[index+1]}_files',os.path.splitext(Convert.FileName(setting['mode'],EpubFilePath[index+1]))[0]+'_tc.epub')
                #Convert.clean(f'{EpubFilePath[index+1]}_files')
        else:
            print('\n>> 請將Epub檔案直接拖曳到本程式中執行翻譯\n')
    except Exception as e:
        log.write(f'發生錯誤 : {str(e)}')
        print(f'發生錯誤 : {str(e)}')
        os.system("pause")
if __name__ == '__main__':
    main()
    os.system("pause")