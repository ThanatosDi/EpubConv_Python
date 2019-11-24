import os
import re
import sys

import cchardet as chardet
import cssutils
from bs4 import BeautifulSoup


def get_key(d: dict, value: str):
    """使用 value 搜尋 dict key

    Arguments:
        d {dict} -- dict
        value {str} -- value
    """
    dk = [dk for dk, dv in d.items() if value in dv]
    if dk:
        return dk[0]
    return None


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def encoding(file_path):
    """ Return file encoding """
    with open(file_path, "rb") as f:
        msg = f.read()
        result = chardet.detect(msg)
        return result

def replace(content, replace_string_list = [' '], new=''):
    '''將 content 中 replace_string_list 的字串變為空
    
    Arguments:
        content {[type]} -- [description]
    '''
    for string in replace_string_list:
        content = content.replace(string, new)
    return content

def selectors_check(CSSs:list):
    """進行 css selectors 搜尋，尋找 html {*} 的 css
    
    Arguments:
        CSSs {list} -- css 檔的絕對路徑
    
    Returns:
        None: 找不到有該 css selectors
        str : css 檔的絕對路徑
    """    
    parser = cssutils.CSSParser()
    for CSS in CSSs:
        CSSStyle = parser.parseFile(CSS)
        for selector in CSSStyle.cssRules.rulesOfType(1):
            if selector.selectorText=='html':
                return CSS
    return None


def opf_modify(file, regex, content):
    """opf 橫直轉換
    
    Arguments:
        file {str} -- opf 檔路徑
        regex {regex} -- 正規表示法
        content {str} -- 符合 regex 的字串替換成本字串
    """    
    with open(file, 'r+', encoding=encoding(file)['encoding']) as f:
        content = re.sub(regex, content, f.read())
        f.seek(0)
        f.truncate()
        f.write(content)

def add_style(file, relpath):
    style_attrs = {
        'rel': 'stylesheet',
        'type': 'text/css',
        'href': relpath
    }
    with open(file, 'r+', encoding=encoding(file)['encoding']) as f:
        bs4 = BeautifulSoup(f.read(), 'html.parser')
        if not bs4.find_all('link', {'href': re.compile(r".*EPUBConv_style\.css")}):
            style_tag = bs4.new_tag('link')
            for attrs, value in style_attrs.items():
                style_tag.attrs[attrs] = value
            bs4.head.append(style_tag)
            f.seek(0)
            f.truncate()
            f.write(bs4.prettify())
