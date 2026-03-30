# 南网E文件解析工具 - 打包说明

## 概述

本文档说明如何将南网E文件解析工具打包成Windows MSI安装程序。

## 依赖要求

1. **Python 3.8+** - 主要开发环境
2. **PyInstaller 6.18.0** - 用于打包Python应用程序
3. **WiX Toolset 3.11+** - 用于创建MSI安装程序
4. **PySide6 6.10.2** - Qt界面库

## 安装依赖

```bash
# 安装Python依赖
pip install PySide6==6.10.2 pyinstaller==6.18.0

# 安装WiX Toolset
# 从 https://wixtoolset.org/ 下载并安装
# 确保candle.exe和light.exe在PATH中
```

## 打包过程

### 1. 准备资源文件

确保以下文件存在于`resources/`目录：

- `spic_logo.png` - 应用程序图标
- `spic-logo.svg` - SVG版本的logo
- `eparser_empty.db` - 空数据库文件
- `folder.png`, `parse.png`, `database.png`, `export.png` - UI图标
- `refresh.png`, `delete.png`, `clear.png` - UI图标

### 2. 运行构建脚本

```bash
python build_installer.py
```

或者使用批处理脚本：

```bash
build_installer.bat
```

### 3. 构建输出

构建完成后，将生成以下文件：

- `EFileParser_Setup.msi` - Windows安装程序
- `dist/EFileParser/EFileParser.exe` - 可执行文件
- `dist/EFileParser/` - 完整的应用程序目录

## 安装程序功能

### 安装内容

1. **主程序**: `EFileParser.exe`
2. **空数据库**: `eparser_empty.db`
3. **Logo文件**: `spic_logo.png`, `spic-logo.svg`
4. **开始菜单快捷方式**
5. **桌面快捷方式**
6. **注册表项**: 用于安装检测

### 安装选项

- **安装位置**: 默认安装到 `C:\Program Files\南网E文件解析工具\`
- **用户界面**: 中文界面，使用微软雅黑字体
- **安装范围**: 全机器安装（需要管理员权限）

## 测试安装程序

1. 双击 `EFileParser_Setup.msi` 运行安装程序
2. 按照安装向导步骤进行安装
3. 安装完成后，检查：
   - 程序是否在开始菜单中
   - 桌面快捷方式是否创建
   - 程序是否能正常运行

## 卸载

1. 通过控制面板 -> 程序和功能卸载
2. 或者运行: `msiexec /x EFileParser_Setup.msi`

## 问题排除

### 缺少依赖

如果构建失败，检查是否所有依赖都已安装：

```bash
python --version
pip show PySide6 pyinstaller
candle.exe --version
light.exe --version
```

### 权限问题

确保以管理员身份运行构建脚本，因为MSI安装程序需要管理员权限。

### 文件路径问题

确保所有资源文件路径正确，并且文件存在。

## 版本信息

- **应用程序版本**: 2.2.0
- **打包脚本版本**: 1.0.0
- **最后更新**: 2026年1月24日

## 联系信息

- **开发单位**: 国家电投昆明生产运营中心
- **作者**: 陈丰
- **联系电话**: 0871-65666603
- **技术支持**: 0871-65666603

## 许可信息

© 2026 国家电投昆明生产运营中心 版权所有
<task_progress>
- [x] Analyze current qt_app_v2.py program
- [x] Optimize and beautify the code
- [ ] Enhance the UI design
- [ ] Test the application
- [ ] Prepare empty database and logo
- [ ] Create Windows MSI installer
</task_progress>
</write_to_file>