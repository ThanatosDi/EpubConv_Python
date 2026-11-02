import os

import chardet
from loguru import logger


def file_encoding(file: str):
    """
    檔案編碼偵測函式，根據檔案路徑偵測檔案編碼。

    Args:
        file (str): 檔案路徑。

    Returns:
        str: 偵測出的檔案編碼。

    Raises:
        FileNotFoundError: 檔案不存在
    """
    if os.path.exists(file) == False:
        raise FileNotFoundError(f'檔案 {file} 不存在')
    with open(file, 'rb') as f:
        detect = chardet.detect(f.read())
    logger.debug(detect)
    return detect['encoding']


def dict_to_css_text(css_dict: dict) -> str:
    """
    將 CSS style Dict 轉換為 CSS 文字。

    Args:
        css_dict (dict): CSS style 的 Dict 格式。

    Returns:
        str: CSS 的文字格式。
    """
    return '\n'.join(['%s: %s;' % (key, value)
                      for (key, value) in css_dict.items()])
