import requests


class GoogleTranslate:
    def __init__(self, sl: str = 'auto', tl: str = 'zh-TW', value=None):
        self.SourceLang = sl
        self.TargetLang = tl
        self.value = value
        self.__response = self.__translate

    @property
    def __translate(self):
        with requests.get(f'https://translate.googleapis.com/translate_a/single?client=gtx&sl={self.SourceLang}&tl={self.TargetLang}&dt=t&ie=utf-8&oe=utf-8&q={self.value}') as req:
            if req.status_code != 200:
                return None
            req.encoding = 'utf-8'
            return req.text

    @property
    def toList(self):
        """Return data value from str to list
        """
        return self.__response.replace(']', '').replace('[', '').replace("\"", '').split(',')

    @property
    def toDict(self):
        t = self.toList
        d = {
            "sourcelang": t[1],
            "targetlang": t[0],
            "unknow": t[2:]
        }
        return d

    @property
    def response(self):
        """Return response data
        """
        return self.__response
