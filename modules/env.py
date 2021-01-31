import os

from dotenv import load_dotenv


class Env():
    def __init__(self):
        load_dotenv(override=True)

    @property
    def ENGINE(self) -> str:
        """回傳轉換引擎

        Returns:
            str: 回傳轉換引擎，有'opencc', 'fanhuaji', 'fanhuaji_async'
        """        
        ALLOW = ['opencc', 'fanhuaji', 'fanhuaji_async']
        value = os.getenv('ENGINE', 'opencc').lower()
        if value not in ALLOW:
            return 'opencc'
        return value

    @property
    def CONVERTER(self) -> str:
        ALLOW = ['t2s', 's2t', 'tw2s', 's2tw']
        value = os.getenv('CONVERTER', 's2t').lower()
        if value not in ALLOW:
            return 's2t'
        converter = {'t2s': 'Simplified',
                     's2t': 'Traditional',
                     'tw2s': 'China',
                     's2tw': 'Taiwan'
                     }
        if self.ENGINE in ['fanhuaji', 'fanhuaji_async']:
            return converter.get(value, 's2t')
        return value

    @property
    def FORMAT(self) -> str:
        ALLOW = ['straight', 'horizontal']
        value = os.getenv('CONVERTER', 'horizontal').lower()
        if value not in ALLOW:
            return 'horizontal'
        return value

    @property
    def LOG_LEVEL(self) -> str:
        ALLOW = ['CRITICAL', 'ERROR', 'WARNING',
                 'INFO', 'DEBUG', 'NOTSET']
        value = os.getenv('LOG_LEVEL', 'INFO')
        if value.upper() not in ALLOW:
            return 'INFO'
        return value

    @property
    def SYSLOG_LEVEL(self) -> str:
        ALLOW = ['CRITICAL', 'ERROR', 'WARNING',
                 'INFO', 'DEBUG', 'NOTSET']
        value = os.getenv('SYSLOG_LEVEL', 'INFO')
        if value.upper() not in ALLOW:
            return 'INFO'
        return value

    @property
    def FILE_CHECK(self) -> bool:
        value = os.getenv('FILE_CHECK', 'true').lower()
        if value == 'true':
            return True
        return False

    @property
    def ENABLE_PAUSE(self) -> bool:
        value = os.getenv('ENABLE_PAUSE', 'true').lower()
        if value == 'true':
            return True
        return False
