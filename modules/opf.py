import re


class Opf():
    def __init__(self, converter):
        self.converter = converter

    def lang(self, file:str):
        """改變 content.opf <dc:language> 內容值

        Args:
            file ([str]): content.opf 的絕對路徑
        """        
        ZH = ['s2t', 's2tw', 'Traditional', 'Taiwan']
        CN = ['t2s', 'tw2s', 'Simplified', 'China']
        regex = re.compile(
            r"<dc:language>[\S]*</dc:language>", re.IGNORECASE)
        content = open(file, encoding='utf-8').read()
        if self.converter in ZH:
            content = re.sub(
                regex, '<dc:language>zh-Hant-TW</dc:language>', content)
        if self.converter in CN:
            content = re.sub(
                regex, '<dc:language>zh-Hans-CN</dc:language>', content)
        open(file, 'w', encoding='utf-8').write(content)
