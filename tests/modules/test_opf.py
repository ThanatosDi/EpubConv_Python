import pytest

from app.modules.opf import OPF

OPF_CONTENT = '''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>测试书籍</dc:title>
    <dc:language>{language}</dc:language>
  </metadata>
</package>
'''


class TestOPF():
    @pytest.mark.parametrize('converter, expected', [
        ('s2t', 'zh-Hant-TW'),
        ('s2tw', 'zh-Hant-TW'),
        ('s2twp', 'zh-Hant-TW'),
        ('t2s', 'zh-Hans-CN'),
        ('tw2s', 'zh-Hans-CN'),
        ('tw2sp', 'zh-Hans-CN'),
    ])
    def test_language(self, tmp_path, config, converter, expected):
        config(converter=converter)
        opf_path = tmp_path / 'content.opf'
        opf_path.write_text(OPF_CONTENT.format(language='zh-CN'), encoding='utf-8')

        OPF(str(opf_path)).language()

        assert opf_path.read_text(encoding='utf-8') == OPF_CONTENT.format(language=expected)

    def test_language_case_insensitive_tag(self, tmp_path, config):
        config(converter='s2twp')
        opf_path = tmp_path / 'content.opf'
        opf_path.write_text('<DC:LANGUAGE>zh</DC:LANGUAGE>', encoding='utf-8')

        OPF(str(opf_path)).language()

        assert opf_path.read_text(encoding='utf-8') == '<dc:language>zh-Hant-TW</dc:language>'
