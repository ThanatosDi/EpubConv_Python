const fs = require('fs')
const zerorpc = require("zerorpc");
const path = require("path");

const client = new zerorpc.Client();
// import Swal from 'app.ui/scripts/sweetalert2.all.min.js'

client.connect("tcp://127.0.0.1:4242");

function ErrorAlert(err) {
    Swal.fire({
        type: 'error',
        title: err,
    })
}
fs.stat('config.ini', (err, stats) => {
    if (err) {
        return 0
    }
    if (stats.isFile('config.ini')) { // do this 
        client.invoke("load", (error, res) => {
            if (error) {
                console.debug(error)
                return ErrorAlert('哦哦...發生錯誤\n')
            }
            document.querySelector('#engine').value = res.engine
            document.querySelector('#engine').click()
            document.querySelector('#file_check').checked = (res.file_check == 'True')
            document.querySelector('#enable_pause').checked = (res.enable_pause == 'True')
            for (key in res) {
                document.querySelector(`#${key}`).value = res[key]
            }
            
        })
    }
});

document.querySelector("#save_btn").addEventListener('click', () => {
    var engine = document.querySelector('#engine').value;
    var converter = document.querySelector('#converter').value;
    var format = document.querySelector('#format').value;
    var loglevel = document.querySelector('#loglevel').value;
    var syslevel = document.querySelector('#syslevel').value;
    var file_check = document.querySelector('#file_check').checked;
    var enable_pause = document.querySelector('#enable_pause').checked;
    items = {
        'engine': engine,
        'converter': converter,
        'format': format,
        'loglevel': loglevel,
        'syslevel': syslevel,
        'file_check': file_check,
        'enable_pause': enable_pause
    }
    client.invoke('save', items, (err, res) => {
        if (err) {
            return ErrorAlert(err.message)
        }
        Swal.fire({
            type: 'success',
            title: '哦耶~保存成功啦~',
        })
    })
});