# Open Packaging Format
import re

from config import config


class OPF():
    def __init__(self, opf_absolute_path: str):
        self.opf_absolute_path = opf_absolute_path

    def language(self) -> None:
        MAPPING = {
            'zh-Hant-TW': ['s2t', 's2tw', 's2twp'],
            'zh-Hans-CN': ['t2s', 'tw2s', 'tw2sp'],
        }
        regex = re.compile(
            r"<dc:language>[\S]*</dc:language>", re.IGNORECASE)
        for __language, __converter in MAPPING.items():
            if config.CONVERTER in __converter:
                language = __language
        content = open(self.opf_absolute_path, encoding='utf-8').read()
        content = re.sub(
            regex, f'<dc:language>{language}</dc:language>', content)
        open(self.opf_absolute_path, 'w', encoding='utf-8').write(content)
