import os
from pathlib import Path

import pytest

from app.modules.epubconv import EPUBConv
from tests.conftest import VERTICAL_STYLES, EpubInspector

VERTICAL_CSS = 'html { color: black; %s }\np { text-indent: 2em; }' % ' '.join(
    f'{key}: {value};' for key, value in VERTICAL_STYLES.items())


def run(epub: Path) -> None:
    """與 main.py 相同的轉換流程"""
    epubconv = EPUBConv(str(epub))
    epubconv.epub_extract()
    content_files = epubconv.epub_file.content_files
    css_files = epubconv.epub_file.css_files
    opf_file = epubconv.epub_file.opf_file
    epubconv.content_convert(content_files)
    epubconv.opf_convert(opf_file)
    epubconv.file_rename(content_files)
    epubconv.writing_format(
        opf_path=opf_file,
        epub_extract_path=epubconv.epub_extract_path,
        css_files=css_files,
        content_files=content_files,
    )
    epubconv.epub_compress()
    epubconv.clean()


def convert(make_epub, config, *, converter='s2twp', format='horizontal', **kwargs) -> EpubInspector:
    config(engine='opencc', converter=converter, format=format, add_suffix=True)
    epub = make_epub('book.epub', **kwargs)
    run(epub)
    return EpubInspector(epub.parent / f'book_{converter}.epub')


def assert_vertical(book: EpubInspector):
    assert book.page_progression_direction == 'rtl'
    for page in book.pages:
        styles = book.applied_vertical_styles(page)
        assert styles == VERTICAL_STYLES, f'{page} 沒有套用完整直書樣式'
    for css in book.css_files:
        assert css in book.manifest.values(), f'{css} 不在 OPF manifest 中'


def assert_horizontal(book: EpubInspector):
    assert book.page_progression_direction is None
    for page in book.pages:
        assert book.applied_vertical_styles(page) == {}, f'{page} 仍套用直書樣式'


class TestEpubFile():
    def test_files(self, make_epub):
        epub = make_epub()
        epubconv = EPUBConv(str(epub))
        epub_file = epubconv.epub_file
        extract_path = Path(f'{epub}_files')

        assert sorted(epub_file.content_files) == sorted([
            os.path.abspath(extract_path / 'OEBPS' / 'Text' / 'chapter1.xhtml'),
            os.path.abspath(extract_path / 'OEBPS' / 'Text' / 'chapter2.xhtml'),
            os.path.abspath(extract_path / 'OEBPS' / 'content.opf'),
            os.path.abspath(extract_path / 'OEBPS' / 'toc.ncx'),
        ])
        assert epub_file.css_files == [
            os.path.abspath(extract_path / 'OEBPS' / 'Styles' / 'style.css')]
        assert epub_file.opf_file == os.path.abspath(extract_path / 'OEBPS' / 'content.opf')
        assert epub_file.epub_extract_path == f'{epub}_files/'
        assert epubconv.epub_extract_path == f'{epub}_files/'

    def test_no_css(self, make_epub):
        epubconv = EPUBConv(str(make_epub(css=None)))
        assert epubconv.epub_file.css_files == []

    def test_clean(self, make_epub):
        epub = make_epub()
        epubconv = EPUBConv(str(epub))
        epubconv.epub_extract()
        assert Path(f'{epub}_files').is_dir()

        epubconv.clean()

        assert not Path(f'{epub}_files').exists()

    def test_clean_without_extract(self, make_epub):
        epubconv = EPUBConv(str(make_epub()))
        epubconv.clean()


class TestConvertContent():
    def test_s2twp(self, make_epub, config):
        book = convert(make_epub, config, converter='s2twp')

        chapter1 = book.read('OEBPS/Text/chapter1.xhtml')
        chapter2 = book.read('OEBPS/Text/chapter2.xhtml')
        assert '這是一本簡體中文的小說，內容講述了一個少年的冒險故事。' in chapter1
        assert '軟體和記憶體都是計算機的重要組成部分。' in chapter2
        assert '第一章 簡體中文' in book.read('OEBPS/toc.ncx')
        assert book.language == 'zh-Hant-TW'

    def test_t2s(self, make_epub, config):
        book = convert(make_epub, config, converter='t2s')

        assert book.language == 'zh-Hans-CN'
        assert '这是一本简体中文的小说' in book.read('OEBPS/Text/chapter1.xhtml')

    def test_original_file_untouched(self, make_epub, config):
        config(engine='opencc', converter='s2twp', format='horizontal', add_suffix=True)
        epub = make_epub('book.epub')
        original = epub.read_bytes()

        run(epub)

        assert epub.read_bytes() == original
        assert not Path(f'{epub}_files').exists()


class TestConvertFormat():
    def test_horizontal(self, make_epub, config):
        book = convert(make_epub, config, format='horizontal')
        assert_horizontal(book)

    def test_vertical_to_horizontal(self, make_epub, config):
        book = convert(make_epub, config, format='horizontal',
                       css=VERTICAL_CSS, page_progression_direction='rtl')

        assert_horizontal(book)
        assert 'color: black' in book.read('OEBPS/Styles/style.css')

    def test_vertical_css_without_html(self, make_epub, config):
        book = convert(make_epub, config, format='vertical')

        assert_vertical(book)
        assert 'OEBPS/Styles/epubconv_custom.css' in book.manifest.values()

    def test_vertical_css_with_html(self, make_epub, config):
        book = convert(make_epub, config, format='vertical',
                       css='html { color: black; }\np { text-indent: 2em; }')

        assert_vertical(book)
        assert 'OEBPS/Styles/epubconv_custom.css' not in book.names

    def test_vertical_no_css(self, make_epub, config):
        book = convert(make_epub, config, format='vertical', css=None)

        assert_vertical(book)
        assert book.css_files == ['OEBPS/Styles/epubconv_custom.css']

    @pytest.mark.xfail(strict=True, reason='已知問題：CSS 已有 html 選擇器時，沒有 link 該 CSS 的頁面不會套用直書樣式')
    def test_vertical_css_with_html_partially_linked(self, make_epub, config):
        book = convert(make_epub, config, format='vertical',
                       css='html { color: black; }', linked_chapters=('chapter1',))

        assert_vertical(book)

    @pytest.mark.xfail(strict=True, reason='已知問題：OPF 不在 OEBPS/ 時，新增的 CSS 位置與 manifest 的 href 不一致')
    def test_vertical_opf_at_root(self, make_epub, config):
        book = convert(make_epub, config, format='vertical', opf_dir='', css=None)

        assert_vertical(book)
