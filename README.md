[![GitHub release](https://img.shields.io/github/release/Kutinging/EpubConv_Python.svg?style=plastic)](https://github.com/Kutinging/EpubConv_Python/releases)  
# EPubConv_Python EPub簡繁橫直互轉 Rewrite
<!--[![GitHub release](https://img.shields.io/github/release/ThanatosDi/EpubConv_Python.svg?style=plastic)](https://github.com/ThanatosDi/EpubConv_Python/releases)  -->
  
Used python convert epub file from Simplified Chinese to Traditional Chinese on windows  
使用 Python 撰寫，epub 檔案繁簡橫直互轉 
# Download 下載
https://github.com/ThanatosDi/EpubConv_Python/releases

# Todo 待辦事項
 - [x] EPub
     - [x] 檔案格式檢查
     - [x] 檔案解壓縮
     - [x] 檔案名稱轉換
     - [x] 轉換 content.opf 語言標籤
     - [x] 重新命名已轉換檔案
     - [ ] 格式橫直轉換
     - [x] 檔案包裝壓縮
     - [x] 清除暫存檔
 - [x] 轉換引擎
     - [x] OpenCC
     - [x] zhconvert 繁化姬
     - [ ] GoogleTranslate
 - [x] 其他
     - [x] 自動判斷檔案編碼 

# Usage 使用
直接將 epub 檔案拖曳至 epubconv.exe 上即可立即翻譯 epub 檔案
# Update history 更新歷史
詳細雜湊碼請看 release 頁面的 virustotal 結果
* [v2.0.0](https://github.com/ThanatosDi/EpubConv_Python/releases/tag/2.0.0)
  * 加入繁化姬轉換引擎
  *  修改讀取檔案方法，由程式自動判斷檔案編碼(1.X.X版本為強制使用utf-8格式讀取)
  * 修改 log 記錄檔記錄功能，只會紀錄當下轉換的輸出，下次轉換時會將記錄清空重新記錄
  * 修改 config 的設定方法，讓使用者更容易設定(裡面包含幫助請記得看)
  * 修改 epub 檔案格式驗證
  * 暫時拔除橫直轉換功能
# Known Bugs目前已知問題

# Third Party Library 第三方庫
感謝以下作者及團隊，沒有你們這個軟體就不會出現  
[OpenCC](https://github.com/BYVoid/OpenCC) by BYVoid  
[OpenCC-Python](https://github.com/yichen0831/opencc-python) by yichen0831  
[zhconvert 繁化姬](https://zhconvert.org/) by Fanhuaji organizations (rexx0520建議)  
[Google Translate](https://cloud.google.com/translate/) by Google  
