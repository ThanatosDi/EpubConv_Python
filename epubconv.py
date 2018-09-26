# -*- coding: utf8 -*-
import zipfile,os,glob,sys,shutil,chardet

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
        config_file = os.path.join(__WorkPath__,'opencc', CONFIG_DIR, config)
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
            dict_file = os.path.join(__WorkPath__,'opencc', DICT_DIR, filename)
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

__WorkPath__ = os.path.abspath(os.path.join(sys.argv[0],os.path.pardir)) #程式絕對路徑
__EpubFilePath__ = sys.argv #epub檔案絕對路徑
__OpenCCPath__ = __WorkPath__ + '\opencc\\' #opencc絕對路徑

def OpenCC_Check():
    if os.path.exists(__OpenCCPath__) and os.path.isfile( __OpenCCPath__ + 'dictionary\\STCharacters.txt' ) and os.path.isfile( __OpenCCPath__ + 'dictionary\\STPhrases.txt' ) and os.path.isfile( __OpenCCPath__ + 'config\\s2t.json' ):
        return True
    else:
        return False

def File_Check(_FileName_):
    if os.path.splitext(_FileName_)[-1] == '.epub' :
        return True
    else:
        return False

def Unzip(_FilePath_):
    """ 將 epub 使用 zip 方式解壓縮，並取得epub中的書籍簡介、內文檔案絕對路徑"""  
    try:
        zip_file = zipfile.ZipFile( _FilePath_ )  
        _UnZipPath_ = _FilePath_ + '_files\\'
        if os.path.isdir( _FilePath_ + "_files"):  
            pass  
        else:  
            os.mkdir( _FilePath_ + "_files")  
        for names in zip_file.namelist():  
            zip_file.extract(names, _FilePath_ + "_files/")
        _FileList_ = [os.path.abspath( _UnZipPath_ + filename) for filename in zip_file.namelist() if any(filename.endswith(FileExtension) for FileExtension in ['ncx', 'opf', 'xhtml', 'html', 'htm', 'txt'])]
        zip_file.close()
        return _FileList_
    except:
        print('Cannot unzip file.')
        return False

def Zip(_ZipPath_,_FileName_):
    """使用zip壓縮所有檔案成為epub zipepub(檔案資料夾,壓縮後的檔案名稱')  """
    try:
        if os.path.isfile(_FileName_):
            pass
        else:
            FileList = []  
            if os.path.isfile(_ZipPath_):  
                FileList.append(_ZipPath_)  
            else :  
                for root, _dirs, files in os.walk(_ZipPath_):  
                    for name in files:  
                        FileList.append(os.path.join(root, name))  
                
            zf = zipfile.ZipFile(_FileName_, 'w', zipfile.zlib.DEFLATED)  
            for tar in FileList:  
                arcname = tar[len(_ZipPath_):]
                zf.write(tar,arcname)  
            zf.close()
            if os.path.isfile(_FileName_):
                print('  刪除暫存檔案')
                CleanTmp(_ZipPath_)
                return True
            else:
                print('  刪除暫存檔案')
                CleanTmp(_ZipPath_)
                print('Zip2epub failed.')
                return False
    except:
        print('Zip2epub failed.')
        return False

def CleanTmp( _DirPath_ ):
    shutil.rmtree(_DirPath_)

def Convert(_FileList_):
    openCC = OpenCC('s2t')
    try:
        for File in _FileList_:
            Encoding(File) #轉換編碼:將簡體中文編碼轉utf-8編碼
            FileRead = open(File,'r',encoding='utf-8')
            FileLines = FileRead.readlines()
            FileRead.close()
            with open( File + '.new','w',encoding='UTF-8') as FileWrite:
                print(' Convert ' + File + ' Now')
                for Line in FileLines:
                    converted = openCC.convert(Line)
                    FileWrite.write(converted)
        return True
    except Exception as error:
        Error = '\n《 Convert 【' + File + '】 failed.》\n Error Messages : '+str(error)
        print(Error)
        Log(Error)
        return False

def Rename(_FileList_):
    try:
        for _FileName_ in _FileList_:
            print('  正在重新命名 '+ _FileName_ +'.new 到 '+ _FileName_)
            os.remove(_FileName_)
            os.rename(_FileName_+'.new',_FileName_)
        return True
    except Exception as error:
        Error = '\n正在重新命名 '+ _FileName_ +'.new 到 '+ _FileName_ + '失敗'
        print(Error)
        Log(Error)
        return False

def FileNameS2T( _FilePath_ ):
    openCC = OpenCC('s2t')
    Path = os.path.dirname( _FilePath_ )
    FileName = openCC.convert(os.path.basename( _FilePath_ ))
    return os.path.join(Path,FileName)


def Encoding(_File_):
    try:
        with open( _File_ , 'rb') as f:
            encoding = (chardet.detect(f.read())['encoding']).upper()
            print( _File_ +' encoding is '+ encoding)
            if encoding=='GB18030' or encoding=='GBK' or encoding=='GB2312':
                encoding = 'GB18030'
                print('Open file use '+encoding+' encoding')
                with open( _File_ , 'r', encoding=encoding) as FileRead:
                    FileLines = FileRead.readlines()
                    with open( _File_ ,'w',encoding='UTF-8') as FileWrite:
                        print(' Convert ' + _File_ + ' encoding from '+encoding+' to UTF-8 Now')
                        for Line in FileLines:
                            FileWrite.write(Line)
            elif encoding=='UTF-8':
                print('File already UTF-8 encoding\nPass')
                pass
        return encoding
    except Exception as error:
        print(str(error))
        return False
        
def Log(ErrorMessages):
    with open( 'epubconv.log','w',encoding='UTF-8') as LogWrite:
        LogWrite.write(ErrorMessages)

def main():
    if len(__EpubFilePath__) > 1:
        for x in range(len(__EpubFilePath__)-1):
            if OpenCC_Check() and File_Check(__EpubFilePath__[x+1]):
                FileList = Unzip(__EpubFilePath__[x+1])
                if not FileList == None and Convert(FileList):
                    print('File S2T Success')
                    if Rename(FileList):
                        print('File Rename Success')
                        if Zip( __EpubFilePath__[x+1] + '_files' ,os.path.splitext(FileNameS2T(__EpubFilePath__[x+1]))[0]+'_tc.epub'):
                            print('File Convert Success')
                        else:
                            CleanTmp(__EpubFilePath__[x+1] + '_files')
                            print(' File Convert Failed \n Maybe The File Exist')
                            break
                    else:
                        CleanTmp(__EpubFilePath__[x+1] + '_files')
                        print('File Rename Failed')
                        break
                else:
                    CleanTmp(__EpubFilePath__[x+1] + '_files')
                    print('File S2T Failed or filelist is none')
                    break
            else:
                print('Miss OpenCC config or OpenCC dictionary')
                break
    else:
        print('  請將Epub檔案直接拖曳到本程式中執行翻譯  ')


if __name__ == '__main__':
    main()
    os.system("pause")