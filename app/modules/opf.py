# Open Packaging Format
import re

from config.config import Config


class OPF():
    def __init__(self, opf_absolute_path: str):
        self.opf_absolute_path = opf_absolute_path

    def language(self) -> None:
        """
        設定 OPF 檔案中的語言代碼。

        根據 Config 中的 CONVERTER 設定，從 MAPPING 中找到對應的語言代碼，
        並將其寫入 OPF 檔案中。

        Returns:
            None
        """
        MAPPING = {
            'zh-Hant-TW': ['s2t', 's2tw', 's2twp'],
            'zh-Hans-CN': ['t2s', 'tw2s', 'tw2sp'],
        }
        regex = re.compile(
            r"<dc:language>[\S]*</dc:language>", re.IGNORECASE)
        for __language, __converter in MAPPING.items():
            if Config.CONVERTER in __converter:
                language = __language
        content = open(self.opf_absolute_path, encoding='utf-8').read()
        content = re.sub(
            regex, f'<dc:language>{language}</dc:language>', content)
        open(self.opf_absolute_path, 'w', encoding='utf-8').write(content)
