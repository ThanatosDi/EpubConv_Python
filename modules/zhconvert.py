# 繁化姬模組
import requests
from modules.utils.error import RequestError


class ZhConvert:
    """ 繁化姬模組 """

    def __init__(self, converter):
        """  """
        self.API = 'https://api.zhconvert.org'
        self.converter = converter

    def __request(self, endpoint: str, playload):
        with requests.get(f'{self.API}{endpoint}', data=playload) as req:
            if req.status_code != 200:
                raise RequestError('Request error.')
            req.encoding = 'utf-8'
            return req.text

    def __check(self):
        allow_converter = ["Simplified",
                           "Traditional",
                           "China",
                           "Taiwan",
                           "WikiSimplified",
                           "WikiTraditional"]

    def convert(self, text):
        playload = {
            'text': text,
            'converter': self.converter
        }
        test = self.__request('/convert', playload)
        print(test)
