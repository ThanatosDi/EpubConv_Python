from dotenv import dotenv_values

from app.Enums.ConverterEnum import ConverterEnum
from app.Enums.EngineEnum import EngineEnum
from app.Enums.FormatEnum import FormatEnum
from app.modules.logger import Logger

config = dotenv_values("config.ini")
logger = Logger(
    'Setting configuration',
    config.get('log_level', 'debug').upper(),
    config.get('syslog_level', 'info').upper(),
)


def __engine() -> str:
    engine = config.get('engine', 'opencc').lower()
    if not EngineEnum.has_value(engine):
        logger.warning(f'轉換引擎不存在: {engine}，故使用預設引擎: opencc')
        config['engine'] = 'opencc'
        return 'opencc'
    return engine


def __converter() -> str:
    converter = config.get('converter', 's2t').lower()
    if not ConverterEnum.converter.value.has_name(converter):
        logger.warning(f'轉換器不存在: {converter}，故使用預設轉換器: s2t')
        config['converter'] = 's2t'
        return 's2t'
    return converter


def __format() -> str:
    _format = config.get('format', 'horizontal').lower()
    if not FormatEnum.has_value(_format):
        logger.warning(f'格式不存在: {_format}，故使用預設格式: horizontal(橫書)')
        config['format'] = 'horizontal'
        return 'horizontal'
    return _format


ENGINE = __engine()
CONVERTER = __converter()
FORMAT = __format()
LOGLEVEL = config.get('loglevel', 'debug').upper()
STDLEVEL = config.get('stdlevel', 'info').upper()
