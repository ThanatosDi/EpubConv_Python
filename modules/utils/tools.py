def get_key(d: dict, value:str):
    """使用 value 搜尋 dict key
    
    Arguments:
        d {dict} -- dict
        value {str} -- value
    """
    return [dk for dk, dv in d.items() if value in dv]