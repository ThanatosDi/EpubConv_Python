import cssutils
import pytest
from bs4 import BeautifulSoup

from app.modules.writing_format import OpfFormat, StyleFile, WritingFormat
from tests.conftest import VERTICAL_STYLES

SPINE_OPF = '''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0">
  <spine toc="ncx"{attr}>
    <itemref idref="chapter1"/>
  </spine>
</package>
'''


def write_opf(tmp_path, direction=None):
    opf_path = tmp_path / 'content.opf'
    attr = f' page-progression-direction="{direction}"' if direction else ''
    opf_path.write_text(SPINE_OPF.format(attr=attr), encoding='utf-8')
    return opf_path


def spine_direction(opf_path):
    soup = BeautifulSoup(opf_path.read_text(encoding='utf-8'), 'xml')
    return soup.select_one('spine').get('page-progression-direction')


def html_rule(css_path):
    sheet = cssutils.CSSParser().parseFile(str(css_path))
    for rule in sheet.cssRules.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
        if rule.selectorText == 'html':
            return {key: rule.style.getPropertyValue(key) for key in rule.style.keys()}
    return None


class TestOpfFormat():
    def test_add_vertical_attribute(self, tmp_path):
        opf_path = write_opf(tmp_path)
        OpfFormat(str(opf_path)).add_vertical_attribute()
        assert spine_direction(opf_path) == 'rtl'

    def test_add_vertical_attribute_keep_rtl(self, tmp_path):
        opf_path = write_opf(tmp_path, 'rtl')
        OpfFormat(str(opf_path)).add_vertical_attribute()
        assert spine_direction(opf_path) == 'rtl'

    @pytest.mark.parametrize('direction', ['rtl', 'ltr'])
    def test_remove_vertical_attribute(self, tmp_path, direction):
        opf_path = write_opf(tmp_path, direction)
        OpfFormat(str(opf_path)).remove_vertical_attribute()
        assert spine_direction(opf_path) is None

    def test_remove_vertical_attribute_without_attribute(self, tmp_path):
        opf_path = write_opf(tmp_path)
        OpfFormat(str(opf_path)).remove_vertical_attribute()
        assert spine_direction(opf_path) is None

    @pytest.mark.parametrize('direction, expected', [
        ('rtl', 'vertical'),
        (None, 'horizontal'),
    ])
    def test_check_writing_format(self, tmp_path, direction, expected):
        opf_path = write_opf(tmp_path, direction)
        assert OpfFormat(str(opf_path)).check_writing_format == expected


class TestStyleFile():
    def test_selector_exist(self, tmp_path):
        no_html = tmp_path / 'a.css'
        no_html.write_text('p { color: red; }', encoding='utf-8')
        with_html = tmp_path / 'b.css'
        with_html.write_text('html { color: black; }', encoding='utf-8')

        assert StyleFile().selector_exist('html', [str(no_html), str(with_html)])
        assert not StyleFile().selector_exist('html', [str(no_html)])
        assert not StyleFile().selector_exist('html', [])

    def test_create_vertical_style(self, tmp_path):
        StyleFile().create_vertical_style(str(tmp_path), WritingFormat().vertical_styles)

        css_path = tmp_path / 'OEBPS' / 'Styles' / 'epubconv_custom.css'
        rule = html_rule(css_path)
        for key, value in VERTICAL_STYLES.items():
            assert rule[key] == value
        assert rule['margin'] == '0'
        assert rule['padding'] == '0'

    def test_append_vertical_style(self, tmp_path):
        with_html = tmp_path / 'with_html.css'
        with_html.write_text('html { color: black; }\np { text-indent: 2em; }', encoding='utf-8')
        no_html = tmp_path / 'no_html.css'
        no_html.write_text('p { text-indent: 2em; }', encoding='utf-8')

        StyleFile().append_vertical_style(
            [str(with_html), str(no_html)], WritingFormat().vertical_styles)

        rule = html_rule(with_html)
        assert rule['color'] == 'black'
        for key, value in VERTICAL_STYLES.items():
            assert rule[key] == value
        assert no_html.read_text(encoding='utf-8') == 'p { text-indent: 2em; }'

    def test_delete_vertical_style(self, tmp_path):
        css_path = tmp_path / 'style.css'
        styles = ' '.join(f'{key}: {value};' for key, value in VERTICAL_STYLES.items())
        css_path.write_text(f'html {{ color: black; {styles} }}', encoding='utf-8')

        StyleFile().delete_vertical_style([str(css_path)], WritingFormat().vertical_styles)

        assert html_rule(css_path) == {'color': 'black'}

    def test_delete_vertical_style_without_html(self, tmp_path):
        css_path = tmp_path / 'style.css'
        css_path.write_text('p { text-indent: 2em; }', encoding='utf-8')

        StyleFile().delete_vertical_style([str(css_path)], WritingFormat().vertical_styles)

        assert css_path.read_text(encoding='utf-8') == 'p { text-indent: 2em; }'


class TestWritingFormat():
    def test_invalid_format(self, config):
        config(format='diagonal')
        with pytest.raises(ValueError, match='diagonal'):
            WritingFormat().format('', '', [], [])
