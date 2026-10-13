import pytest

from app.enums.converter_enum import (Converter, ConverterEnum,
                                      FanhuajiConverter, FilenameConverter,
                                      OpenccConverter)
from app.enums.engine_enum import EngineEnum
from app.enums.format_enum import FormatEnum

CONVERTERS = ['s2t', 's2tw', 's2twp', 't2s', 'tw2s', 'tw2sp']


class TestConverterEnum():
    @pytest.mark.parametrize('converter', CONVERTERS)
    def test_opencc_has_value(self, converter):
        assert OpenccConverter.has_value(converter)

    def test_opencc_has_value_invalid(self):
        assert not OpenccConverter.has_value('s2hk')

    @pytest.mark.parametrize('converter, expected', [
        ('s2t', 'Traditional'),
        ('s2tw', 'Traditional'),
        ('s2twp', 'Taiwan'),
        ('t2s', 'Simplified'),
        ('tw2s', 'Simplified'),
        ('tw2sp', 'China'),
    ])
    def test_fanhuaji_mapping(self, converter, expected):
        assert getattr(FanhuajiConverter, converter).value == expected

    @pytest.mark.parametrize('converter, expected', [
        ('s2t', 's2t'),
        ('s2tw', 's2t'),
        ('s2twp', 's2t'),
        ('t2s', 't2s'),
        ('tw2s', 't2s'),
        ('tw2sp', 't2s'),
    ])
    def test_filename_mapping(self, converter, expected):
        assert getattr(FilenameConverter, converter).value == expected

    @pytest.mark.parametrize('converter', CONVERTERS)
    def test_converter_has_name(self, converter):
        assert Converter.has_name(converter)

    def test_converter_has_name_invalid(self):
        assert not Converter.has_name('s2hk')

    def test_converter_enum_members(self):
        assert ConverterEnum.opencc.value is OpenccConverter
        assert ConverterEnum.fanhuaji.value is FanhuajiConverter
        assert ConverterEnum.filename.value is FilenameConverter
        assert ConverterEnum.converter.value is Converter


class TestEngineEnum():
    @pytest.mark.parametrize('engine', ['opencc', 'fanhuaji', 'fanhuaji_async'])
    def test_has_value(self, engine):
        assert EngineEnum.has_value(engine)

    def test_has_value_invalid(self):
        assert not EngineEnum.has_value('google')


class TestFormatEnum():
    @pytest.mark.parametrize('format', ['horizontal', 'vertical'])
    def test_has_value(self, format):
        assert FormatEnum.has_value(format)

    def test_has_value_invalid(self):
        assert not FormatEnum.has_value('diagonal')
