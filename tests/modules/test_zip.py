import zipfile

import pytest

from app.modules.zip import ZIP


class TestZIP():
    def test_extract(self, make_epub):
        epub = make_epub()

        ZIP.extract(str(epub))

        extract_path = epub.parent / f'{epub.name}_files'
        assert (extract_path / 'mimetype').read_text() == 'application/epub+zip'
        assert (extract_path / 'OEBPS' / 'content.opf').exists()
        assert (extract_path / 'OEBPS' / 'Text' / 'chapter1.xhtml').exists()

    def test_extract_existing_folder(self, make_epub):
        epub = make_epub()
        (epub.parent / f'{epub.name}_files').mkdir()

        ZIP.extract(str(epub))

        assert (epub.parent / f'{epub.name}_files' / 'mimetype').exists()

    def test_zipfile(self, make_epub):
        epub = make_epub()
        with ZIP.zipfile(str(epub)) as z:
            assert isinstance(z, zipfile.ZipFile)
            assert 'mimetype' in z.namelist()

    @pytest.mark.parametrize('converter, expected', [
        ('s2t', '簡體書名.epub'),
        ('s2twp', '簡體書名.epub'),
        ('t2s', '简体书名.epub'),
        ('tw2sp', '简体书名.epub'),
    ])
    def test_convert_filename(self, tmp_path, config, converter, expected):
        config(converter=converter)
        source = '简体书名.epub' if converter.startswith('s') else '簡體書名.epub'
        assert ZIP.convert_filename(str(tmp_path / source)) == expected

    def test_convert_filename_unknown_converter(self, tmp_path, config):
        config(converter='unknown')
        assert ZIP.convert_filename(str(tmp_path / '简体书名.epub')) == '簡體書名.epub'

    @pytest.mark.parametrize('add_suffix, expected', [
        (True, '簡體書名_s2twp.epub'),
        (False, '簡體書名.epub'),
    ])
    def test_compress(self, make_epub, config, add_suffix, expected):
        config(converter='s2twp', add_suffix=add_suffix)
        epub = make_epub('简体书名.epub')
        ZIP.extract(str(epub))

        ZIP.compress(str(epub))

        output = epub.parent / expected
        with zipfile.ZipFile(epub) as original, zipfile.ZipFile(output) as compressed:
            assert sorted(compressed.namelist()) == sorted(original.namelist())
            for name in original.namelist():
                assert compressed.read(name) == original.read(name)

    @pytest.mark.xfail(strict=True, reason='已知問題：compress 沒有把 mimetype 放在第一個並以不壓縮方式儲存')
    def test_compress_mimetype_first_and_stored(self, make_epub, config):
        config(converter='s2twp', add_suffix=True)
        epub = make_epub('book.epub')
        ZIP.extract(str(epub))

        ZIP.compress(str(epub))

        with zipfile.ZipFile(epub.parent / 'book_s2twp.epub') as z:
            first = z.infolist()[0]
            assert first.filename == 'mimetype'
            assert first.compress_type == zipfile.ZIP_STORED
