from pathlib import Path

import pytest

from epubconv import Config, convert_epub
from epubconv.modules.epubconv import EPUBConv
from tests.conftest import EpubInspector


@pytest.fixture(autouse=True)
def defaults(config):
    config(engine='opencc', converter='s2t', format='horizontal', add_suffix=True)


class TestConvertEpub():
    def test_use_config(self, make_epub):
        epub = make_epub('简体书名.epub')

        output = convert_epub(epub)

        assert output == epub.parent / '簡體書名_s2t.epub'
        book = EpubInspector(output)
        assert '這是一本簡體中文的小說' in book.read('OEBPS/Text/chapter1.xhtml')
        assert not Path(f'{epub}_files').exists()

    def test_options_override_config_once(self, make_epub):
        epub = make_epub('book.epub')

        output = convert_epub(epub, converter='s2twp', format='vertical', add_suffix=False)

        assert output == epub.parent / 'book.epub'
        book = EpubInspector(output)
        assert book.language == 'zh-Hant-TW'
        assert book.page_progression_direction == 'rtl'
        # 選項只在這次轉換生效
        assert (Config.CONVERTER, Config.FORMAT, Config.ADD_SUFFIX) == ('s2t', 'horizontal', True)

    def test_accept_str_and_relative_path(self, make_epub, monkeypatch):
        epub = make_epub('book.epub')
        monkeypatch.chdir(epub.parent)

        output = convert_epub('book.epub')

        assert output == epub.parent / 'book_s2t.epub'

    @pytest.mark.parametrize('option', [
        {'engine': 'google'},
        {'converter': 'xxx'},
        {'format': 'diagonal'},
    ])
    def test_invalid_option_raises_before_extract(self, make_epub, option):
        epub = make_epub('book.epub')

        with pytest.raises(ValueError, match=next(iter(option.values()))):
            convert_epub(epub, **option)

        assert not Path(f'{epub}_files').exists()
        assert (Config.ENGINE, Config.CONVERTER, Config.FORMAT) == ('opencc', 's2t', 'horizontal')

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            convert_epub(tmp_path / 'missing.epub')

    def test_failure_cleans_temp_files(self, make_epub, mocker):
        epub = make_epub('book.epub')
        mocker.patch.object(EPUBConv, 'content_convert', side_effect=RuntimeError('boom'))

        with pytest.raises(RuntimeError, match='boom'):
            convert_epub(epub)

        assert not Path(f'{epub}_files').exists()
        assert not (epub.parent / 'book_s2t.epub').exists()
