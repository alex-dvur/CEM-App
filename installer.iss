[Setup]
AppName=MOGLabs Motorised Cateye (CEM)
AppVersion=1.0.2
AppPublisher=MOGLabs
DefaultDirName={autopf}\MOGLabs\CEM
DefaultGroupName=MOGLabs CEM
OutputBaseFilename=CEM_Installer_v1.0.2
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\CEM\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\MOGLabs CEM"; Filename: "{app}\CEM.exe"
Name: "{autodesktop}\MOGLabs CEM"; Filename: "{app}\CEM.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\CEM.exe"; Description: "Launch MOGLabs CEM"; Flags: nowait postinstall skipifsilent
