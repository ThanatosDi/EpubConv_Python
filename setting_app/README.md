# EPubConv Setting App

快速建立或設定 EPubConv 設定檔  
## v1.0.0  
### 建立開發環境
1. 前置動作請到 [electron-zerorpc](https://github.com/ThanatosDi/electron-zerorpc) 建立編譯 nodejs zeromq 環境
2. `npm install`
3. `npm run rebuild`
4. `npm start` (確認是否可以正常啟動 electron)
5. `pip install -r ./requirements.txt`
6. 開心修改程式囉~~
7. `pyinstaller ./api.py` (打包 api.py 檔案成執行檔)
8. `npm run win32` (打包整個 UI 及 js 檔)  
   
    提醒：建議另外開一個資料夾將以下內容放入  
       1. app.ui/*  
       2. dist/*  
       3. node_modules/*  
       4. package-lock.json  
       5. package.json  
       6. main.js  
    並在該資料夾中執行 `npm run win32` 打包 electron 專案  
    以免包入不必要檔案
### 檔案用途
* app.ui (存放 UI 介面)
* api.py (Python 後端操作)
* dist/api (api.py 使用 pyinstaller 打包後的執行檔)
* setting.py (連結檔，做為開啟 setting app 的入口檔)
* setting.exe (setting.py 打包後的執行檔)

