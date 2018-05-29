; 
; OpenCC GUI (AutoHotkey Version)
;
; Created on 28-12-2017
;
; Coded by SeIsland
;
; Version 1.0.0
;
; Posted on puresoftapps.blogspot.com
;

#NoEnv
#SingleInstance Force
SetWorkingDir %A_ScriptDir%
Loop %A_WorkingDir%\*.json

 json .= (( json <> "" ) ? "|" : "" ) A_LoopFileName
 
Gui Add, Text, x16 y16 w120 h23 +0x200, Input Folder
Gui Add, Edit, vinput_path x16 y48 w340 h21
Gui Add, Button, gInputBrowse x376 y48 w80 h23, Browse
Gui Add, Text, x16 y80 w120 h23 +0x200, Output Folder
Gui Add, Edit, voutput_path x16 y120 w340 h21
Gui Add, Button, gOutputBrowse x376 y120 w80 h23, Browse
Gui Add, Text, x16 y160 w120 h23 +0x200, Configurations
Gui Add, DropDownList, vjsonselected x144 y160 w91, %json%
Gui Add, Button, gConvert x376 y160 w80 h23, Convert

Gui Show, w479 h205, OpenCC GUI (AutoHotkey Version)
Return

InputBrowse:
FileSelectFolder, input_path,,, Select Input Folder
GuiControl,, input_path, %input_path%
Return
OutputBrowse:
FileSelectFolder, output_path,,, Select Output Folder
GuiControl,, output_path, %output_path%
Return

Convert:
GuiControlGet, input_path
GuiControlGet, output_path
GuiControlGet, jsonselected
If (input_path="")
{
MsgBox,, Error, Input directory is not set.
Return
}
else if !FileExist(input_path)
{
MsgBox,, Error, Input directory is not found.
Return
}
If (output_path="")
{
MsgBox,, Error, Output directory is not set.
Return
}
If (jsonselected="")
{
MsgBox,, Error, Configuration is not set.
Return
}
Loop Files, %input_path%\*.*, R
{
 StringReplace, output_filepath, A_LoopFileFullPath, %input_path%, %output_path%, A
 StringReplace, output_subfolder_path, output_filepath, \%A_LoopFileName%,, A
 FileCreateDir, %output_subfolder_path%
 Progress, %a_index%, %a_loopfilename%, Converting..., Progress
 runwait, opencc.exe "-i" "%A_LoopFileFullPath%" "-o" "%output_filepath%" "-c" "%jsonselected%", %A_WorkingDir%, Hide
 Sleep, 50
}
Progress, off
return


GuiEscape:
GuiClose:
    ExitApp
