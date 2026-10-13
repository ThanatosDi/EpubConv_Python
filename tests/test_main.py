import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.conftest import EpubInspector

MAIN = Path(__file__).resolve().parent.parent / 'main.py'


def run_main(*epubs: Path, **settings) -> subprocess.CompletedProcess:
    """執行 main.py，以環境變數覆寫 config.ini 的設定"""
    env = os.environ | {
        'ENGINE': 'opencc',
        'ENABLE_PAUSE': 'false',
        'ADD_SUFFIX': 'true',
        'PYTHONIOENCODING': 'utf-8',
    } | {key.upper(): value for key, value in settings.items()}
    return subprocess.run(
        [sys.executable, str(MAIN), *map(str, epubs)],
        env=env, capture_output=True, encoding='utf-8', timeout=120,
    )


class TestMain():
    @pytest.mark.parametrize('format, direction', [
        ('horizontal', None),
        ('vertical', 'rtl'),
    ])
    def test_convert(self, make_epub, format, direction):
        epub = make_epub('简体书名.epub')

        process = run_main(epub, converter='s2twp', format=format)

        assert process.returncode == 0, process.stderr
        book = EpubInspector(epub.parent / '簡體書名_s2twp.epub')
        assert '這是一本簡體中文的小說' in book.read('OEBPS/Text/chapter1.xhtml')
        assert book.language == 'zh-Hant-TW'
        assert book.page_progression_direction == direction
        assert not Path(f'{epub}_files').exists()

    def test_multiple_files(self, make_epub):
        first = make_epub('第一本.epub')
        second = make_epub('第二本.epub')

        process = run_main(first, second, converter='s2t', format='horizontal')

        assert process.returncode == 0, process.stderr
        assert (first.parent / '第一本_s2t.epub').exists()
        assert (second.parent / '第二本_s2t.epub').exists()

    @pytest.mark.xfail(strict=True, reason='已知問題：以相對路徑執行 main.py 時，os.chdir("") 會引發 OSError')
    def test_relative_main_path(self, make_epub):
        epub = make_epub('book.epub')
        env = os.environ | {'ENGINE': 'opencc', 'ENABLE_PAUSE': 'false'}

        process = subprocess.run(
            [sys.executable, 'main.py', str(epub)],
            cwd=MAIN.parent, env=env, capture_output=True, timeout=120,
        )

        assert process.returncode == 0
