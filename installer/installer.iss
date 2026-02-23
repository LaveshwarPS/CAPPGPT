# Inno Setup Installer Script for CAPP Turning Planner
# 
# This script creates a professional Windows installer (.exe) for the CAPP application.
#
# Download Inno Setup from: https://jrsoftware.org/isdl.php
# Usage: "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer/installer.iss
#
# Output: Creates CAPP_Turning_Planner_Setup_X.X.X.exe in the dist/ folder

#define MyAppName "CAPP Turning Planner"
#define MyAppPublisher "CAPP Project"
#define MyAppPublisherURL "https://github.com/yourusername/capp-ai-project"
#define MyAppExeName "CAPP_Turning_Planner.exe"
#define MyAppVersion "1.0.0"
#define SourcePath "..\dist\CAPP_Turning_Planner"

[Setup]
; Installer settings
AppId={{3E5C8FD1-F8B5-4B8D-A1C2-E9F3B5D7C2A9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppPublisherURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=yes
OutputDir=..\dist
OutputBaseFilename=CAPP_Turning_Planner_Setup_{#MyAppVersion}
SetupIconFile=..\installer\icon.ico
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; Create desktop shortcut
Name: "desktopicon"; Description: "{cm:CreateDesktopIconTask}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

; Create Quick Launch bar shortcut (for Windows 7 and older)
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIconTask}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Copy the PyInstaller-generated exe and all dependencies
Source: "{#SourcePath}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Copy README and documentation
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"

; Uninstall shortcut
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

; Desktop shortcut (if user selects the task)
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

; Quick Launch shortcut (if user selects the task)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: quicklaunchicon

[Run]
; Run the app after installation (optional)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
{ Optional: Add code to check for Python 3.12 before installation }
function InitializeSetup(): Boolean;
begin
  Result := True;
  
  { Check for Python 3.12+ }
  if not FileExists('C:\Program Files\Python312\python.exe') and 
     not FileExists('C:\Program Files (x86)\Python312\python.exe') then
  begin
    if not FileExists(ExpandConstant('{localappdata}\Programs\Python\Python312\python.exe')) then
    begin
      MsgBox('Python 3.12 or later is required. Please install Python 3.12 from https://www.python.org/downloads/ first.', 
        mbError, MB_OK);
      Result := False;
    end;
  end;
end;
