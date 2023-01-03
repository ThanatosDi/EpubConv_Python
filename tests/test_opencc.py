from app.engines.opencc import OpenCCEngine


class TestOpenCC():
    @classmethod
    def setup_class(cls):
        cls.opencc = OpenCCEngine()

    def test_opencc_convert_s2t(self):
        text = self.opencc.convert('s2t', '使用 Python 撰写，epub 档案繁简横直互转')
        assert text == '使用 Python 撰寫，epub 檔案繁簡橫直互轉'

    def test_opencc_convert_t2s(self):
        text = self.opencc.convert('t2s', '使用 Python 撰寫，epub 檔案繁簡橫直互轉')
        assert text == '使用 Python 撰写，epub 档案繁简横直互转'

    def test_opencc_convert_s2twp(self):
        text = self.opencc.convert('s2twp', '内存')
        assert text == '記憶體'

    def test_opencc_convert_tw2sp(self):
        text = self.opencc.convert('tw2sp', '記憶體')
        assert text == '内存'
