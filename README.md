# EpubConv_Python Epub簡繁橫直互轉
[![GitHub release](https://img.shields.io/github/release/Kutinging/EpubConv_Python.svg?style=plastic)](https://github.com/Kutinging/EpubConv_Python/releases)  
  
Used python convert epub file from Simplified Chinese to Traditional Chinese on windows  
使用 Python 撰寫，轉換epub檔案從簡體中文到繁體中文  
# Download 下載
https://github.com/Kutinging/EpubConv_Python/releases
# Usage 使用
直接將 epub 檔案拖曳至 epubconv.exe 上即可立即翻譯 epub 檔案
# Update history 更新歷史
* 1.0.5.
* 1.0.5.1
  - 修正橫直互轉功能異常
    -  各個epub檔案內容格式不同導致錯誤之修正
  - 修正 log 檔儲存位置錯誤
    -  1.0.5版本為epub檔案所在處新增log檔修正為本程式所在位置新增log檔
* 1.0.5(bata)
  * 新增橫直排互轉功能
    *  目前該功能為測試功能，目前為橫直互轉
* 1.0.4.4(bata)
  * 新增橫排轉直排功能
      * 目前該功能為測試功能，僅有橫轉直，橫直互轉還再努力中
  * 新增 config.json 設定檔
      * 目前該功能為測試功能，由使用者決定要簡轉繁還繁轉簡，不確定是否有BUG
  * 新增 log 記錄功能
      * 將會記錄轉換過程中的錯誤訊息，如發現有BUG請提供log檔及epub電子書到 epubconv@mail.kawai.moe 排除BUG
* 1.0.4.3
  * 修正效率不佳問題
* 1.0.4.2
  * Fix an error occurred when file encoding isn't utf-8.
* 1.0.4.1
  * Fix folder will convert to Traditional Chinese let zip function will fall.
* 1.0.4
  * Fix epub file path has chinese will crash.
  * Change convert program.
* 1.0.3.1
  * Fix 才 will convert to 纔,now will all convert to 才.
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
* 1.0.5.1
  * 無 css 檔案時造成程式拋出例外 List index out of range.
* 1.0.4.2
  * 效率低落問題(1.0.4.3已修復)

# Third Party Library 第三方庫
[OpenCC](https://github.com/BYVoid/OpenCC) by BYVoid  
[OpenCC-Python](https://github.com/yichen0831/opencc-python) by yichen0831  
