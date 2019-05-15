import os
import sys


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
