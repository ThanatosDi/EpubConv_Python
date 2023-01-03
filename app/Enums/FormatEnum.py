from enum import Enum


class FormatEnum(Enum):
    vertical = 'vertical'  # 直書
    horizontal = 'horizontal'  # 橫書

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
