import asyncio
import json
from typing import IO, Any, Callable, Dict, List, Optional, Tuple, Type, Union

import aiohttp
import requests

API = 'https://api.zhconvert.org'


class FanhuajiEngine():
    """繁化姬轉換引擎"""

    def _request(self, endpoint: str, payload: dict):
        with requests.get(f'{API}{endpoint}', data=payload) as response:
            if response.status_code == 200:
                response.encoding = 'utf-8'
                return json.loads(response.text)
            raise RequestError(
                f'zhconvert Request error. status code: {response.status_code}')

    async def _async_request(self, session, endpoint: str, payload: dict):
        async with session.get(f'{API}{endpoint}', data=payload) as response:
            if response.status == 200:
                content = await response.json()
                await session.close()
                return content
            raise AsyncRequestError(
                f'zhconvert AsyncRequest error. status code: {response.status}')

    def _slice(self, content: str) -> Optional[List[str]]:
        """文字內容每 50,000 字進行一次切片處理

        Args:
            content ([str]): 文字內容

        Returns:
            Optional[List[str]]: 回傳為 list 且裡面為切片後的 str
        """
        chunks = []
        chunks_count = len(content)//50_000+1
        for i in range(0, chunks_count):
            chunks.append(content[50_000*i:50_000*(i+1)])
        return chunks

    def convert(self, **kwargs):
        """繁化姬轉換

        API doc : https://docs.zhconvert.org/api/convert/

        Arguments:
            text : 欲轉換的文字\n\n
            converter : 所要使用的轉換器。有 Simplified （簡體化）、 Traditional （繁體化）、 
                        China （中國化）、  Taiwan （台灣化）、WikiSimplified （維基簡體化）、 
                        WikiTraditional （維基繁體化）。\n\n
            ignoreTextStyles : 由那些不希望被繁化姬處理的 "樣式" 以逗號分隔所組成的字串。
                               通常用於保護特效字幕不被轉換，
                               例如字幕組的特效字幕若是以 OPJP 與 OPCN 作為樣式名。
                               可以設定 "OPJP,OPCN" 來作保護。\n\n
            jpTextStyles : 告訴繁化姬哪些樣式要當作日文處理（預設為伺服器端自動猜測）。
                           若要自行設定，則必須另外再加入 *noAutoJpTextStyles 這個樣式。
                           所有樣式以逗號分隔組成字串，
                           例如： "OPJP,EDJP,*noAutoJpTextStyles" 表示不讓伺服器自動猜測，
                           並指定 OPJP 與 EDJP 為日文樣式。\n\n
            jpStyleConversionStrategy : 對於日文樣式該如何處理。 
                                        "none" 表示 無（當成中文處理） 、 "protect" 表示 保護 、 
                                        "protectOnlySameOrigin" 表示 僅保護原文與日文相同的字 、 
                                        "fix" 表示 修正 。\n\n	
            jpTextConversionStrategy : 對於繁化姬自己發現的日文區域該如何處理。 
                                       "none" 表示 無（當成中文處理） 、 "protect" 表示 保護 、 
                                       "protectOnlySameOrigin" 表示 僅保護原文與日文相同的字 、 
                                       "fix" 表示 修正 。\n\n	
            modules : 強制設定模組啟用／停用 。 -1 / 0 / 1 分別表示 自動 / 停用 / 啟用 。
                      字串使用 JSON 格式編碼。使用 * 可以先設定所有模組的狀態。
                      例如：{"*":0,"Naruto":1,"Typo":1} 表示停用所有模組，
                      但啟用 火影忍者 與 錯別字修正 模組。\n\n	
            userPostReplace : 轉換後再進行的額外取代。
                              格式為 "搜尋1=取代1\\n搜尋2=取代2\\n..." 。 
                              搜尋1 會在轉換後再被取代為 取代1 。\n\n	
            userPreReplace : 轉換前先進行的額外取代。
                             格式為 "搜尋1=取代1\\n搜尋2=取代2\\n..." 。 
                             搜尋1 會在轉換前先被取代為 取代1 。\n\n	
            userProtectReplace : 保護字詞不被繁化姬修改。
                                 格式為 "保護1\\n保護2\\n..." 。 
                                 保護1 、 保護2 等字詞將不會被繁化姬修改。
        """
        ALLOW_KEYS = [
            'text',
            'converter',
            'ignoreTextStyles',
            'jpTextStyles',
            'jpStyleConversionStrategy',
            'jpTextConversionStrategy',
            'modules',
            'userPostReplace',
            'userPreReplace',
            'userProtectReplace',
        ]
        error_keys = [key for key in kwargs.keys() if key not in ALLOW_KEYS]
        if error_keys:
            raise FanhuajiInvalidKey(f"Invalid key: {', '.join(error_keys)}")
        if kwargs.get('text', None) is None or kwargs.get('converter', None) is None:
            raise FanhuajiMissNecessarykey(f"Miss necessary key")
        response = self._request('/convert', kwargs)
        return self._text(response)

    def _text(self, response) -> Union[None, str]:
        if response['code'] != 0:
            return None
        return response['data']['text']

    async def async_convert(self, **kwargs):
        ALLOW_KEYS = [
            'text',
            'converter',
            'ignoreTextStyles',
            'jpTextStyles',
            'jpStyleConversionStrategy',
            'jpTextConversionStrategy',
            'modules',
            'userPostReplace',
            'userPreReplace',
            'userProtectReplace',
        ]
        error_keys = [key for key in kwargs.keys() if key not in ALLOW_KEYS]
        if error_keys:
            raise FanhuajiInvalidKey(f"Invalid key: {', '.join(error_keys)}")
        content = kwargs.get('text', None)
        converter = kwargs.get('converter', None)
        if content is None or converter is None:
            raise FanhuajiMissNecessarykey(f"Miss necessary key")
        session = aiohttp.ClientSession()
        chunks = self._slice(kwargs.get('text'))
        texts = []
        for chunk in chunks:
            payload = {
                'text': chunk,
                'converter': converter
            }
            response = await self._async_request(session, '/convert', payload)
            texts.append(self._text(response))
        return ''.join(texts)


class RequestError(Exception):
    pass


class AsyncRequestError(Exception):
    pass


class FanhuajiInvalidKey(Exception):
    pass


class FanhuajiMissNecessarykey(Exception):
    pass
