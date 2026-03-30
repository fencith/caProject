#define MyAppName "南网102-e文件解析工具"
#define MyAppVersion "2.1.2"
#define MyAppPublisher "国家电投昆明生产运营中心"
#define MyAppExeName "qt_app_v2_restored.exe"

[Setup]
AppId={{SPIC-EFileParser-2.1.2}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=南网102-e文件解析工具_v2.1.2_setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "spic_logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "spic_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
<task_progress>
- [x] Analyze the application structure
- [x] Check for existing build scripts
- [x] Create installation package with PyInstaller
- [x] Include spic_logo.png and spic_icon.ico
- [ ] Test the installation package
</task_progress>
</write_to_file>