# EpubConv_Python Epub簡轉繁
[![GitHub release](https://img.shields.io/github/release/Kutinging/EpubConv_Python.svg?style=plastic)](https://github.com/Kutinging/EpubConv_Python/releases)  
  
Used python convert epub file from Simplified Chinese to Traditional Chinese on windows  
使用 Python 撰寫，轉換epub檔案從簡體中文到繁體中文  
# Download 下載
https://github.com/Kutinging/EpubConv_Python/releases
# Usage 使用
直接將 epub 檔案拖曳至 epubconv.exe 上即可立即翻譯 epub 檔案
# New version hash
* 1.0.4
 * MD5
  * 3997bde2919e966e7629486288d38d63
 * SHA1
  * 34c08dfb792f509edbbf8302f738f7744836334d
 * SHA-256
  * 82f398f232111e9da9c5bd657856b329ec038d213fd8de1dc20e0cea1fbebf0a
# Update history 更新歷史
* 1.0.4
  * Fix epub file path has chinese will crash
  * Change convert program
* 1.0.3.1
  * Fix 才 will convert to 纔,now will all convert to 才
* 1.0.3
  * Simplified Chinese file name will convert failed.
  * Fix vcruntime140.dll error in windows 10 1803 version.(Cancel use upx.)
* 1.0.2  
  Fix bug
  * Chinese file name can't convert.
  * file name has blank will return error.
* 1.0.1  
  First version release.

# Known Bugs目前已知問題
* 如epub路徑有非英文會造成程式無法辨識路徑造成錯誤(如有建議解法還請大大提供m(_  _)m)

# Third Party Library 第三方庫
[OpenCC](https://github.com/BYVoid/OpenCC) by BYVoid
[OpenCC-Python](https://github.com/yichen0831/opencc-python) by yichen0831
