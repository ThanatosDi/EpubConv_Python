from dotenv import dotenv_values

from app.modules.logger import Logger

config = dotenv_values("config.ini")
logger = Logger(
    'Setting configuration',
    config.get('log_level', 'debug').upper(),
    config.get('syslog_level', 'info').upper(),
)

def __engine() -> str:
    ALLOW = ['opencc', 'fanhuaji', 'fanhuaji_async']
    engine = config.get('engine', 'opencc').lower()
    if engine not in ALLOW:
        logger.warning(f'轉換引擎不存在: {engine}，故使用預設引擎: opencc')
        config['engine'] = 'opencc'
        return 'opencc'
    return engine

def __converter() -> str:
    ALLOW = ['t2s', 's2t', 'tw2s', 's2tw', 'tw2sp', 's2twp']
    converter = config.get('converter', 's2t').lower()
    if converter not in ALLOW:
        logger.warning(f'轉換器不存在: {converter}，故使用預設轉換器: s2t')
        config['converter'] = 's2t'
        return 's2t'
    return converter

def __format() -> str:
    ALLOW = ['straight', 'horizontal']
    format = config.get('format', 'horizontal').lower()
    if format not in ALLOW:
        logger.warning(f'格式不存在: {format}，故使用預設格式: horizontal(水平)')
        config['format'] = 'horizontal'
        return 'horizontal'
    return format


ENGINE = __engine()
CONVERTER = __converter()
FORMAT = __format()
LOGLEVEL = config.get('loglevel', 'debug').upper()
STDLEVEL = config.get('stdlevel', 'info').upper()


