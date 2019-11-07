const { app, BrowserWindow, Menu, ipcMain, dialog, globalShortcut, Tray } = require('electron')
const path = require('path')
const child_process = require('child_process')
const fs = require('fs')
// const zerorpc = require('zerorpc')


// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let win
let aboutView

// let template = [
//   {
//     label: '重新整理',
//     accelerator: 'CmdOrCtrl+R',
//     click: function (item, focusedWindow) {
//       reloadWindow(item, focusedWindow)
//     }
//   }, {
//     label: "幫助",
//     submenu: [{
//       label: '關於本程式',
//       click: async () => {
//         aboutWindow()
//       }
//     }]
//   }
// ]

// const menu = Menu.buildFromTemplate(template)

// 重新整理頁面
function reloadWindow(item, focusedWindow) {
  if (focusedWindow) {
    // on reload, start fresh and close any old
    // open secondary windows
    if (focusedWindow.id === 1) {
      BrowserWindow.getAllWindows().forEach(function (win) {
        if (win.id > 1) {
          win.close()
        }
      })
    }
    focusedWindow.reload()
  }
}

// 建立瀏覽器視窗
function createWindow() {
  win = new BrowserWindow({
    width: 760 + 16,
    height: 680,
    webPreferences: {
      nodeIntegration: true,
    },
    maximizable: false,
    icon: 'app.ico',
    minWidth: 510 + 32,
    minHeight: 680 + 98,
    maxWidth: 760 + 32,
    maxHeight: 680 + 98,
    //icon: './icon.png'
  })

  Menu.setApplicationMenu(null)

  // and load the index.html of the app.
  win.loadFile('app.ui/index.html')

  // 啟用開發者工具
  // win.webContents.openDevTools()

  // 視窗關閉時會觸發。
  win.on('closed', () => {
    // 拿掉 window 物件的參照。如果你的應用程式支援多個視窗，
    // 你可能會將它們存成陣列，現在該是時候清除相關的物件了。
    win = null
  })
}

// 你可以在這個檔案中繼續寫應用程式主程序要執行的程式碼。 
// 你也可以將它們放在別的檔案裡，再由這裡 require 進來。

let pyProc = null
let pyPort = null

const createPyProc = () => {
  let port = '4242'
  // let script = path.join(__dirname, 'api.py')
  // let pyPath = path.join(__dirname, '.env', 'Scripts', 'python.exe')
  // pyProc = child_process.spawn(pyPath, [script, port])

  let script = path.join(__dirname, 'dist', 'api', 'api.exe')
  pyProc = child_process.execFile(script, [port])


  if (pyProc != null) {
    console.log('child process success')
  }
}

const exitPyProc = () => {
  pyProc.kill()
  pyProc = null
  pyPort = null
  console.log('kill python process')
}

// 鍵盤快速鍵觸發事件
function reloadListener() {
  globalShortcut.register('CmdOrCtrl+R', () => {
    reloadWindow(null, BrowserWindow.getFocusedWindow())
  })
}

// 當 Electron 完成初始化，並且準備好建立瀏覽器視窗時
// 會呼叫這的方法
// 有些 API 只能在這個事件發生後才能用。
app.on('ready', () => {
  createWindow()
  createPyProc()
  reloadListener()
})

// 在所有視窗都關閉時結束程式。
app.on('window-all-closed', () => {
  // 在 macOS 中，一般會讓應用程式及選單列繼續留著，
  // 除非使用者按了 Cmd + Q 確定終止它們
  console.debug('main -> app.on("window-all-closed")')
  if (process.platform !== 'darwin') {
    // killByPid(pyProc.pid)
    app.quit()
  }
})

app.on('activate', () => {
  // 在 macOS 中，一般會在使用者按了 Dock 圖示
  // 且沒有其他視窗開啟的情況下，
  // 重新在應用程式裡建立視窗。
  if (win === null) {
    createWindow()
  }
})

app.on('will-quit', () => {
  console.debug('main -> app.on("will-quit")')
  exitPyProc()
  globalShortcut.unregisterAll()
  // tray.destroy()
})
