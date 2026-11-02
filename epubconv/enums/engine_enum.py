from enum import Enum


class EngineEnum(Enum):
    fanhuaji = 'fanhuaji'
    fanhuaji_async = 'fanhuaji_async'
    opencc = 'opencc'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
