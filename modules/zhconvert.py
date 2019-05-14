# 繁化姬模組
import requests
from modules.utils.error import RequestError


class zhconvert:
    """ 繁化姬模組 """

    def __init__(self):
        """  """
        self.API = 'https://api.zhconvert.org'

    @property
    def __request(self):
        with requests.get(self.API) as req:
            if req.status_code != 200:
                raise RequestError('Request error.')
            req.encoding = 'utf-8'
            return req.text
