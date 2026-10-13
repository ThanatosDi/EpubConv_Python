import posixpath
import zipfile
from pathlib import Path

import cssutils
import pytest
from lxml import etree

from config.config import Config

VERTICAL_STYLES = {
    'writing-mode': 'vertical-rl',
    '-webkit-writing-mode': 'vertical-rl',
    '-epub-writing-mode': 'vertical-rl',
    '-epub-line-break': 'strict',
    'line-break': 'strict',
    '-epub-word-break': 'normal',
    'word-break': 'normal',
}

NS = {
    'c': 'urn:oasis:names:tc:opendocument:xmlns:container',
    'o': 'http://www.idpf.org/2007/opf',
}

CONTAINER_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="{opf_path}" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
'''

OPF_XML = '''<?xml version="1.0" encoding="utf-8"?>
<package version="2.0" unique-identifier="BookId" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="BookId">urn:uuid:00000000-0000-0000-0000-000000000000</dc:identifier>
    <dc:title>测试书籍</dc:title>
    <dc:language>zh-CN</dc:language>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
{items}
  </manifest>
  <spine toc="ncx"{spine_attr}>
{itemrefs}
  </spine>
</package>
'''

NCX_XML = '''<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="urn:uuid:00000000-0000-0000-0000-000000000000"/></head>
  <docTitle><text>测试书籍</text></docTitle>
  <navMap>
    <navPoint id="navPoint-1" playOrder="1">
      <navLabel><text>第一章 简体中文</text></navLabel>
      <content src="Text/chapter1.xhtml"/>
    </navPoint>
  </navMap>
</ncx>
'''

XHTML = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>{title}</title>
{links}
</head>
<body>
  <p>{body}</p>
</body>
</html>
'''

CHAPTERS = [
    ('chapter1', '第一章', '这是一本简体中文的小说，内容讲述了一个少年的冒险故事。'),
    ('chapter2', '第二章', '软件和内存都是计算机的重要组成部分。'),
]


def build_epub(
    path: Path,
    *,
    opf_dir: str = 'OEBPS',
    css: str | None = 'p { text-indent: 2em; }',
    linked_chapters: tuple = ('chapter1', 'chapter2'),
    page_progression_direction: str | None = None,
) -> Path:
    """產生測試用的最小 EPUB

    Args:
        path (Path): 輸出的 EPUB 路徑
        opf_dir (str): OPF 所在的資料夾，空字串表示放在根目錄
        css (str | None): Styles/style.css 的內容，None 表示書中沒有 CSS
        linked_chapters (tuple): 有 link style.css 的章節
        page_progression_direction (str | None): spine 的 page-progression-direction

    Returns:
        Path: 輸出的 EPUB 路徑
    """
    def join(*parts):
        return posixpath.join(opf_dir, *parts) if opf_dir else posixpath.join(*parts)

    items, itemrefs = [], []
    files = {}
    for name, title, body in CHAPTERS:
        links = ''
        if css is not None and name in linked_chapters:
            links = '  <link href="../Styles/style.css" rel="stylesheet" type="text/css"/>'
        files[join('Text', f'{name}.xhtml')] = XHTML.format(title=title, links=links, body=body)
        items.append(f'    <item id="{name}" href="Text/{name}.xhtml" media-type="application/xhtml+xml"/>')
        itemrefs.append(f'    <itemref idref="{name}"/>')
    if css is not None:
        files[join('Styles', 'style.css')] = css
        items.append('    <item id="style" href="Styles/style.css" media-type="text/css"/>')
    spine_attr = ''
    if page_progression_direction:
        spine_attr = f' page-progression-direction="{page_progression_direction}"'
    files[join('content.opf')] = OPF_XML.format(
        items='\n'.join(items), itemrefs='\n'.join(itemrefs), spine_attr=spine_attr)
    files[join('toc.ncx')] = NCX_XML

    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml', CONTAINER_XML.format(opf_path=join('content.opf')),
                   compress_type=zipfile.ZIP_DEFLATED)
        for name, content in files.items():
            z.writestr(name, content.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)
    return path


class EpubInspector():
    """讀取轉換後的 EPUB，檢查內容與橫直書格式"""

    def __init__(self, path: Path):
        self.zip = zipfile.ZipFile(path)
        self.names = set(self.zip.namelist())
        container = etree.fromstring(self.zip.read('META-INF/container.xml'))
        self.opf_path = container.find('.//c:rootfile', NS).get('full-path')
        self.opf = etree.fromstring(self.zip.read(self.opf_path))
        base = posixpath.dirname(self.opf_path)
        self.manifest = {
            item.get('id'): posixpath.normpath(posixpath.join(base, item.get('href')))
            for item in self.opf.find('o:manifest', NS)
        }
        self.spine = self.opf.find('o:spine', NS)

    def read(self, name: str) -> str:
        return self.zip.read(name).decode('utf-8')

    @property
    def language(self) -> str:
        return self.opf.find('.//{http://purl.org/dc/elements/1.1/}language').text.strip()

    @property
    def page_progression_direction(self) -> str | None:
        return self.spine.get('page-progression-direction')

    @property
    def pages(self) -> list[str]:
        return [self.manifest[i.get('idref')] for i in self.spine.findall('o:itemref', NS)]

    @property
    def css_files(self) -> list[str]:
        return sorted(n for n in self.names if n.endswith('.css'))

    def linked_css(self, page: str) -> list[str]:
        """頁面 link 的 CSS（以 EPUB 內的路徑表示）"""
        doc = etree.fromstring(self.zip.read(page))
        hrefs = [el.get('href') for el in doc.iter()
                 if isinstance(el.tag, str) and el.tag.endswith('link')
                 and 'stylesheet' in (el.get('rel') or '')]
        return [posixpath.normpath(posixpath.join(posixpath.dirname(page), h)) for h in hrefs]

    def html_vertical_styles(self, css_name: str) -> dict:
        """CSS 中 html 選擇器內的直書屬性"""
        sheet = cssutils.parseString(self.zip.read(css_name))
        styles = {}
        for rule in sheet.cssRules.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
            if rule.selectorText == 'html':
                for key in VERTICAL_STYLES:
                    if value := rule.style.getPropertyValue(key):
                        styles[key] = value
        return styles

    def applied_vertical_styles(self, page: str) -> dict:
        """頁面實際套用到的直書屬性"""
        styles = {}
        for css in self.linked_css(page):
            if css in self.names:
                styles.update(self.html_vertical_styles(css))
        return styles


@pytest.fixture
def make_epub(tmp_path):
    """回傳產生測試 EPUB 的函式"""
    def _make_epub(name: str = 'test.epub', **kwargs) -> Path:
        return build_epub(tmp_path / name, **kwargs)
    return _make_epub


@pytest.fixture
def config(monkeypatch):
    """修改 Config 的設定，測試結束後自動還原"""
    def _set(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setattr(Config, key.upper(), value)
    return _set
