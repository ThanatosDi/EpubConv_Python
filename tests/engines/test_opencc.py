from app.Engines.opencc import OpenCCEngine


class TestOpenCC():
    @classmethod
    def setup_class(cls):
        cls.opencc = OpenCCEngine()

    def test_opencc_convert_s2t(self):
        chapters = [
            {'path': 'test_opencc_convert_s2t.html',
             'content': '使用 Python 撰写，epub 档案繁简横直互转'},
        ]

        ans = [
            {'path': 'test_opencc_convert_s2t.html',
             'content': '使用 Python 撰寫，epub 檔案繁簡橫直互轉'},
        ]
        text = self.opencc.convert('s2t', chapters)
        assert text == ans

    def test_opencc_convert_t2s(self):
        chapters = [
            {'path': 'test_opencc_convert_t2s.html',
             'content': '使用 Python 撰寫，epub 檔案繁簡橫直互轉'},
        ]
        ans = [
            {'path': 'test_opencc_convert_t2s.html',
             'content': '使用 Python 撰写，epub 档案繁简横直互转'},
        ]
        text = self.opencc.convert('t2s', chapters)
        assert text == ans

    def test_opencc_convert_s2twp(self):
        chapters = [
            {'path': 'test_opencc_convert_s2twp.html',
             'content': '内存'},
        ]
        ans = [
            {'path': 'test_opencc_convert_s2twp.html',
             'content': '記憶體'},
        ]
        text = self.opencc.convert('s2twp', chapters)
        assert text == ans

    def test_opencc_convert_tw2sp(self):
        chapters = [
            {'path': 'test_opencc_convert_tw2sp.html',
             'content': '記憶體'},
        ]
        ans = [
            {'path': 'test_opencc_convert_tw2sp.html',
             'content': '内存'},
        ]
        text = self.opencc.convert('tw2sp', chapters)
        assert text == ans
