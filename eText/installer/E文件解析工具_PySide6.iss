[Setup]
AppName=南网E文件解析工具 (PySide6版本)
AppVersion=2.1.2
DefaultDirName={autopf}\南网E文件解析工具_PySide6
DefaultGroupName=南网E文件解析工具_PySide6
OutputDir=installer
OutputBaseFilename=E文件解析工具_PySide6_Setup
SetupIconFile=spic-logo.ico
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin

[Languages]
Name: "chinese"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Files]
Source: "dist\E文件解析工具_PySide6\E文件解析工具_PySide6.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "eparser.db"; DestDir: "{app}"; Flags: ignoreversion
Source: "eparser.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "spic-logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "resources\*"; DestDir: "{app}esources"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\南网E文件解析工具_PySide6"; Filename: "{app}\E文件解析工具_PySide6.exe"; WorkingDir: "{app}"
Name: "{commondesktop}\南网E文件解析工具_PySide6"; Filename: "{app}\E文件解析工具_PySide6.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\E文件解析工具_PySide6.exe"; Description: "启动南网E文件解析工具_PySide6"; Flags: postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\*"

[Messages]
ChineseSimplified.AppName=南网E文件解析工具 (PySide6版本)
ChineseSimplified.AppVersion=版本 2.1.2
ChineseSimplified.AppPublisher=国家电投昆明生产运营中心
ChineseSimplified.AppPublisherURL=http://www.spic.com.cn
ChineseSimplified.AppComments=基于PySide6的南网102-e文件解析工具
ChineseSimplified.AppContact=联系电话: 0871-65666603
ChineseSimplified.UninstallDisplayName=南网E文件解析工具 (PySide6版本)
ChineseSimplified.UninstallDisplayVersion=版本 2.1.2
