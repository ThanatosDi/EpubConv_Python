import pytest

from app.modules.renamer import ReNamer


class TestReNamer():
    def test_rename(self, tmp_path):
        original = tmp_path / 'chapter.xhtml'
        original.write_text('原始內容', encoding='utf-8')
        (tmp_path / 'chapter.xhtml.new').write_text('轉換後內容', encoding='utf-8')

        ReNamer(str(original)).rename()

        assert original.read_text(encoding='utf-8') == '轉換後內容'
        assert not (tmp_path / 'chapter.xhtml.new').exists()

    def test_converted_file_missing(self, tmp_path):
        original = tmp_path / 'chapter.xhtml'
        original.write_text('原始內容', encoding='utf-8')

        with pytest.raises(FileNotFoundError):
            ReNamer(str(original)).rename()
