import logging
import os
import pathlib

import cssutils
from bs4 import BeautifulSoup
from loguru import logger

from app.Enums.FormatEnum import FormatEnum
from app.Modules.utils import dict_to_css_text, file_encoding
from config.config import Config

cssutils.log.setLevel(logging.CRITICAL)


class WritingFormat():
    @property
    def vertical_styles(self) -> dict:
        """
        回傳包含垂直書寫模式的 CSS 樣式的字典。

        Returns:
            dict: 包含垂直書寫模式的 CSS 樣式的字典。鍵是 CSS 屬性名稱，值是相應的 CSS 屬性值。該字典包含以下屬性：
            - 'writing-mode': 元素的書寫模式。值設置為'vertical-rl'。
            - '-webkit-writing-mode': WebKit 瀏覽器的書寫模式。值設置為'vertical-rl'。
            - '-epub-writing-mode': EPUB 文件的書寫模式。值設置為'vertical-rl'。
            - '-epub-line-break': EPUB 文件的斷行模式。值設置為'strict'。
            - 'line-break': 斷行模式。值設置為'strict'。
            - '-epub-word-break': EPUB 文件的斷詞模式。值設置為'normal'。
            - 'word-break': 斷詞模式。值設置為'normal'。
            - 'margin': 元素的邊距。值設置為0。
            - 'padding': 元素的內距。值設置為0。
        """
        vertical = {
            'writing-mode': 'vertical-rl',
            '-webkit-writing-mode': 'vertical-rl',
            '-epub-writing-mode': 'vertical-rl',
            '-epub-line-break': 'strict',
            'line-break': 'strict',
            '-epub-word-break': 'normal',
            'word-break': 'normal',
            'margin': 0,
            'padding': 0,
        }
        return vertical

    def __insert_css(
        self,
        epub_extract_path: str,
        content_files: list,
    ):
        """
        將 CSS 檔案插入 EPUB 檔案中。

        Args:
            epub_extract_path (str): EPUB 檔案的路徑。
            content_files (list): EPUB 檔案中的內容檔案清單。

        Returns:
            None
        """
        element = BeautifulSoup().new_tag('link')
        element.attrs = {
            'rel': 'stylesheet',
            'href': '../Styles/epubconv_custom.css',
            'type': 'text/css',
        }
        css_abs = pathlib.Path(epub_extract_path).joinpath(
            'OEBPS', 'Styles', 'epubconv_custom.css')
        for content_file in content_files:
            if content_file.endswith(tuple(['.opf', 'ncx'])):
                continue
            logger.debug(f'插入 CSS 檔案: {os.path.basename(content_file)}')
            relpath = os.path.relpath(
                css_abs.parent, pathlib.Path(content_file).parent)
            element.attrs['href'] = pathlib.Path(relpath).joinpath(
                'epubconv_custom.css').as_posix()
            soup = BeautifulSoup(
                open(content_file, encoding=file_encoding(content_file)), 'html.parser')
            soup.head.title.insert_before(element)
            open(content_file, 'w',
                 encoding='utf-8').write(soup.prettify())

    def __insert_opf_item(
        self,
        opf_path: str,
    ) -> None:
        """
        將自定義 CSS 檔案插入 OPF 檔案中。

        Args:
            opf_path (str): OPF 檔案的路徑。

        Returns:
            None
        """
        soup = BeautifulSoup(
            open(opf_path, encoding=file_encoding(opf_path)), 'xml')
        item = soup.new_tag('item')
        item.attrs = {
            'href': 'Styles/epubconv_custom.css',
            'id': 'epubconv_custom.css',
            'media-type': 'text/css',
        }
        soup.manifest.append(item)
        open(opf_path, 'w', encoding='utf-8').write(soup.prettify())

    def format(
        self,
        opf_path: str,
        epub_extract_path: str,
        css_files: str,
        content_files: str,
    ):
        """
        格式化電子書檔案的函數。

        Args:
            opf_path (str): OPF 檔案的路徑。
            epub_extract_path (str): EPUB 解壓縮的路徑。
            css_files (str): CSS 檔案的路徑。
            content_files (str): 內容檔案的路徑。

        Returns:
            None

        Raises:
            ValueError: 當 Config.FORMAT 不在 FormatEnum 中時。
        """
        if not FormatEnum.has_value(Config.FORMAT):
            logger.error(f'{Config.FORMAT} 並非支援的書寫格式')
            raise ValueError(
                f'format "{Config.FORMAT}" is not in FormatEnum')
        match(Config.FORMAT):
            case FormatEnum.vertical.value:  # 直書
                logger.info('將書籍書寫格式轉為直式')
                OpfFormat(opf_path).add_vertical_attribute()
                if any(css_files):
                    logger.debug('found css files in this book.')
                    if StyleFile().selector_exist('html', css_files):
                        logger.debug('found selector "html" in css files.')
                        StyleFile().append_vertical_style(
                            css_files,
                            self.vertical_styles,
                        )
                    else:
                        logger.debug('not found selector "html" in css files.')
                        StyleFile().create_vertical_style(
                            epub_extract_path,
                            self.vertical_styles
                        )
                        self.__insert_css(epub_extract_path, content_files)
                        self.__insert_opf_item(opf_path)
                else:
                    logger.debug('not found any css files in this book.')
                    StyleFile().create_vertical_style(
                        epub_extract_path,
                        self.vertical_styles
                    )
                    self.__insert_css(epub_extract_path, content_files)
                    self.__insert_opf_item(opf_path)

            case FormatEnum.horizontal.value:  # 橫書
                logger.info('將書籍書寫格式轉為橫式')
                OpfFormat(opf_path).remove_vertical_attribute()
                StyleFile().delete_vertical_style(
                    css_files, self.vertical_styles)


class OpfFormat():
    def __init__(self, opf_path: str):
        self.opf_path = opf_path

    def add_vertical_attribute(self) -> None:
        """
        將 'spine' 元素中的 'page-progression-direction' 屬性設定為 'rtl'。

        如果 'spine' 元素中不存在 'page-progression-direction' 屬性，則會將其新增並設定為 'rtl'。

        修改後的 OPF 文件將會被寫回文件。
        """
        encoding = file_encoding(self.opf_path)
        content = open(self.opf_path, 'r', encoding=encoding).read()
        opf = BeautifulSoup(content, 'xml')
        spine = opf.select_one('spine')
        if spine.get('page-progression-direction', '') == '':
            spine['page-progression-direction'] = 'rtl'
        open(self.opf_path, 'w', encoding=encoding).write(opf.prettify())

    def remove_vertical_attribute(self) -> None:
        """
        從OPF文件中刪除 'spine' 元素中的 'page-progression-direction' 屬性。

        這個函數讀取 OPF 文件，如果 'spine' 元素中存在 'page-progression-direction' 屬性並且其值為 'rtl' 或 'ltr'，則將其刪除。然後將修改後的 OPF 文件寫回文件。
        """
        encoding = file_encoding(self.opf_path)
        content = open(self.opf_path, 'r', encoding=encoding).read()
        opf = BeautifulSoup(content, 'xml')
        spine = opf.select_one('spine')
        if spine.get('page-progression-direction', '') in ['rtl', 'ltr']:
            del spine['page-progression-direction']
        open(self.opf_path, 'w', encoding=encoding).write(opf.prettify())

    @ property
    def check_writing_format(
        self,
    ) -> str:
        """從 opf 檔案檢查書籍的書寫格式

        Args:
            opf_path (str): opf 檔案的絕對路徑

        Returns:
            str: 書寫格式 (horizontal 橫書 或 vertical 直書)
        """
        encoding = file_encoding(self.opf_path)
        content = open(self.opf_path, 'r', encoding=encoding).read()
        opf = BeautifulSoup(content, 'xml')
        spine = opf.select_one('spine')
        if spine.get('page-progression-direction', '') in ['rtl', 'ltr']:
            return 'vertical'
        return 'horizontal'


class StyleFile():
    def selector_exist(
        self,
        selector: str,
        css_files: list
    ) -> bool:
        """
        檢查CSS選擇器是否存在於指定的CSS文件中。

        Args:
            selector (str): CSS選擇器。
            css_files (list): CSS文件列表。

        Returns:
            bool: 如果選擇器存在於任何一個CSS文件中，則返回True，否則返回False。
        """
        for css_file in css_files:
            sheet = cssutils.CSSParser().parseFile(css_file)
            for rule in sheet.cssRules.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
                if rule.selectorText == selector:
                    return True
        return False

    def create_vertical_style(
        self,
        epub_extract_path: str,
        vertical_style: dict,
    ) -> None:
        """
        創建直書樣式的 CSS 檔案並寫入直書樣式

        Args:
            epub_extract_path (str): EPUB 解壓縮的絕對路徑。
            vertical_style (str): 直書樣式的 CSS 內容。

        Returns:
            None
        """
        logger.debug('創建直書樣式的 CSS 檔案')
        styles_dir_path = os.path.join(epub_extract_path, 'OEBPS', 'Styles')
        if not os.path.exists(styles_dir_path):
            os.makedirs(styles_dir_path)
        css_file = os.path.join(styles_dir_path, 'epubconv_custom.css')
        css = cssutils.CSSParser().parseString('')
        style = cssutils.css.CSSStyleRule(
            selectorText='html', style=dict_to_css_text(vertical_style))
        css.insertRule(style, index=0)
        with open(css_file, 'wb') as f:
            f.write(css.cssText)

    def delete_vertical_style(
        self,
        css_files: list,
        vertical_styles: dict
    ):
        """
        刪除指定CSS文件中的垂直樣式。

        Args:
            css_files (list): CSS文件列表。
            vertical_styles (dict): 垂直樣式的鍵值對。

        Returns:
            None
        """
        rule_list: cssutils.css.CSSRuleList
        rule: cssutils.css.CSSStyleRule
        parser = cssutils.CSSParser()

        for css_file in css_files:
            logger.debug(f'讀取 css: {os.path.basename(css_file)}')
            css = parser.parseFile(css_file)
            rule_list = css.cssRules
            if 'html' not in [rule.selectorText
                              for rule in rule_list.rulesOfType(cssutils.css.CSSRule.STYLE_RULE)]:
                continue
            for rule in rule_list.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
                if rule.selectorText == 'html':
                    for name in vertical_styles.keys():
                        if name in rule.style.keys():
                            del rule.style[name]
            open(css_file, 'wb').write(css.cssText)

    def append_vertical_style(
        self,
        css_files: list,
        vertical_styles: dict,
    ):
        """
        新增指定CSS文件中的垂直樣式。

        Args:
            css_files (list): CSS文件列表。
            vertical_styles (dict): 垂直樣式的鍵值對。

        Returns:
            None
        """
        rule_list: cssutils.css.CSSRuleList
        rule: cssutils.css.CSSStyleRule
        parser = cssutils.CSSParser()

        for css_file in css_files:
            logger.debug(f'讀取 css: {os.path.basename(css_file)}')
            css = parser.parseFile(css_file)
            rule_list = css.cssRules
            if 'html' not in [rule.selectorText
                              for rule in rule_list.rulesOfType(cssutils.css.CSSRule.STYLE_RULE)]:
                continue
            for rule in rule_list.rulesOfType(cssutils.css.CSSRule.STYLE_RULE):
                if rule.selectorText == 'html':
                    for key, value in vertical_styles.items():
                        rule.style[key] = value
            open(css_file, 'wb').write(css.cssText)
