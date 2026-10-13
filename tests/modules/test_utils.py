import codecs

import pytest

from app.modules.utils import dict_to_css_text, file_encoding

TEXT = '<?xml version="1.0"?><html><body><p>这是一本简体中文的小说，内容讲述了一个少年的冒险故事。</p></body></html>'


class TestFileEncoding():
    @pytest.mark.parametrize('encoding', ['utf-8', 'utf-8-sig', 'gb18030'])
    def test_detect(self, tmp_path, encoding):
        file = tmp_path / 'chapter.xhtml'
        file.write_bytes(TEXT.encode(encoding))
        detected = file_encoding(str(file))
        assert codecs.lookup(detected).name == codecs.lookup(encoding).name
        assert file.read_bytes().decode(detected) == TEXT

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            file_encoding(str(tmp_path / 'not_exist.xhtml'))


class TestDictToCssText():
    def test_convert(self):
        css = dict_to_css_text({'writing-mode': 'vertical-rl', 'margin': 0})
        assert css == 'writing-mode: vertical-rl;\nmargin: 0;'

    def test_empty(self):
        assert dict_to_css_text({}) == ''
