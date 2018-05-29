# -*- coding: utf8 -*-
from opencc import OpenCC 
import zipfile,os,glob,sys,shutil

WorkPath = os.path.abspath(os.path.join(sys.argv[0],os.path.pardir)) #程式絕對路徑
EpubFilePath = sys.argv #epub檔案絕對路徑
opencc_path = WorkPath+'/opencc/' #opencc絕對路徑
UnZipPath = ''
def main():
    if(len(EpubFilePath)>1):
        for x in range(len(EpubFilePath)-1):
            UnZipPath = EpubFilePath[x+1]+'_files/'
            epubconv(EpubFilePath[x+1],UnZipPath)
            zip2epub(UnZipPath,getEpubFileName(EpubFilePath[x+1])+'_tc.epub')
            print(getEpubFileName(EpubFilePath[x+1])+'.epub 轉換成功')
    else:
        print('  請將Epub檔案直接拖曳到本程式中執行翻譯  ')
def getEpubFileName(epub_file_path):
    """ 取得epub檔案名稱 不包含副檔名及路徑 檢查檔案格式是否為epub """
    try:
        FileName = os.path.basename(epub_file_path) #ex: 1.epub
        return FileName.split('.epub', 1)[0]
    except:
        print('  This is not a epub file.')
def epubconv(file_path,convert_path):
    try:
        if not(os.path.exists(opencc_path+'opencc.exe')):
            raise IOError
        """ 將 epub 使用 zip 方式解壓縮，並取得epub中的書籍簡介、內文檔案絕對路徑"""  
        zip_file = zipfile.ZipFile(file_path)  
        if os.path.isdir(file_path + "_files"):  
            pass  
        else:  
            os.mkdir(file_path + "_files")  
        for names in zip_file.namelist():  
            zip_file.extract(names,file_path + "_files/")
        file_list = [os.path.abspath(convert_path+filename) for filename in zip_file.namelist() if any(filename.endswith(FileExtension) for FileExtension in ['ncx', 'opf', 'xhtml', 'html', 'htm', 'txt'])]
        zip_file.close()
        for file_name in file_list:
            convert(file_name)
            replace(file_name)
        #print(file_list)
    except IOError:
        print('  請確認 OpenCC 資料夾與本程式在同一目錄.')
        os.system('pause')
        sys.exit(0)
    except:
        print('Unzip failed.')
def zip2epub(dirname,epubname):
    """使用zip壓縮所有檔案成為epub zipepub(檔案資料夾,壓縮後的檔案名稱')  """
    try:
        filelist = []  
        if os.path.isfile(dirname):  
            filelist.append(dirname)  
        else :  
            for root, _dirs, files in os.walk(dirname):  
                for name in files:  
                    filelist.append(os.path.join(root, name))  
            
        zf = zipfile.ZipFile(epubname, "w", zipfile.zlib.DEFLATED)  
        for tar in filelist:  
            arcname = tar[len(dirname):]
            zf.write(tar,arcname)  
        zf.close()
        print('  刪除暫存檔案')
        shutil.rmtree(dirname)
    except:
        print('Zip2epub failed.')
def convert(file_name):
    """ 調用外部程式 opencc 進行檔案翻譯 """
    try:
        convert_command = opencc_path + 'opencc.exe -i "'+file_name+'" -o "'+file_name+'.new" -c '+opencc_path+'s2t.json'
        Object = os.popen(convert_command)
        print('  正在轉換 '+ file_name + ' 檔案中')
        Object.close()
    except:
        print ('  OpenCC failed.')
def replace(file_name):
    try:
        print('  正在重新命名 '+ file_name +'.new 到 '+ file_name)
        os.remove(file_name)
        os.rename(file_name+'.new',file_name)
    except:
        print('  重新命名失敗')


if __name__ == '__main__':
    main()
    os.system("pause")


