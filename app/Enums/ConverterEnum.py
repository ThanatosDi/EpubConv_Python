from enum import Enum


class OpenccConverter(Enum):
    s2t = 's2t'
    s2tw = 's2tw'
    s2twp = 's2twp'
    t2s = 't2s'
    tw2s = 'tw2s'
    tw2sp = 'tw2sp'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class FilenameConverter(Enum):
    s2t = 's2t'
    s2tw = 's2t'
    s2twp = 's2t'
    t2s = 't2s'
    tw2s = 't2s'
    tw2sp = 't2s'


class FanhuajiConverter(Enum):
    s2t = 'Traditional'
    t2s = 'Simplified'
    s2tw = 'Traditional'
    s2twp = 'Taiwan'
    tw2s = 'Simplified'
    tw2sp = 'China'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class Converter(Enum):
    s2t = 's2t'
    s2tw = 's2tw'
    s2twp = 's2twp'
    t2s = 't2s'
    tw2s = 'tw2s'
    tw2sp = 'tw2sp'

    @classmethod
    def has_name(cls, name):
        return name in cls._member_names_


class ConverterEnum(Enum):
    opencc = OpenccConverter
    fanhuaji = FanhuajiConverter
    filename = FilenameConverter
    converter = Converter
