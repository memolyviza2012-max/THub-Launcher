Option Explicit
Dim shell, fso, baseDir, exePath, pythonPath, candidate, command
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
baseDir = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = baseDir
exePath = fso.BuildPath(baseDir, "THub.exe")
If fso.FileExists(exePath) Then
    shell.Run Chr(34) & exePath & Chr(34), 0, False
Else
    pythonPath = ""
    For Each candidate In Array(fso.BuildPath(baseDir, ".venv\Scripts\pythonw.exe"), shell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe"))
        If fso.FileExists(candidate) Then
            pythonPath = candidate
            Exit For
        End If
    Next
    If pythonPath = "" Then pythonPath = "pythonw.exe"
    command = Chr(34) & pythonPath & Chr(34) & " " & Chr(34) & fso.BuildPath(baseDir, "app_pyqt6.py") & Chr(34)
    On Error Resume Next
    shell.Run command, 0, False
    If Err.Number <> 0 Then MsgBox "Cannot launch THub. Install Python with PyQt6, or use the packaged THub.exe.", 48, "THub"
    On Error GoTo 0
End If
