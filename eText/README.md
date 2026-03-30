# E文件解析工具

> 根据《南方电网新能源数据上送规范 V3.3修订版（2022.2月）》及总调水新〔2025〕28号文件开发

## 快速开始

### 方法1：安装使用（推荐）

```bash
# Windows用户
1. 以管理员身份运行 install.bat
2. 双击桌面快捷方式"E文件解析工具"
```

### 方法2：直接运行

```bash
# 进入目录版本
dist/EFileParser/EFileParser.exe

# 或运行单文件版本
dist/EFileParser_Single.exe
```

## 功能特点

✅ **图形化界面** - 使用Qt6开发，美观易用
✅ **6类E文件支持** - FDJZ、SYZXX、ZTXX-QXHJ、DQYC、CDQYC、TJXX
✅ **实时解析** - 快速解析E文件数据
✅ **多标签页展示** - 文件概览、详细数据、原始内容
✅ **报告导出** - 支持导出为文本报告
✅ **无需安装Python** - 已打包为独立EXE文件

## 系统要求

- Windows 10/11 (64位)
- 内存：至少4GB
- 磁盘空间：100MB

## 使用说明

1. 启动程序
2. 点击"选择文件"或拖拽.dat文件
3. 点击"解析"按钮
4. 查看解析结果（三个标签页）
5. 可选择"导出报告"保存结果

## 支持的E文件类型

| 类型 | 说明 |
|------|------|
| FDJZ | 风机/光伏单机信息 |
| SYZXX | 升压站信息 |
| ZTXX-QXHJ | 总体信息和气象环境 |
| DQYC | 短期功率预测 |
| CDQYC | 超短期功率预测 |
| TJXX | 统计信息 |

## 项目结构

```
D:\001\eText/
├── dist/                       # 可执行程序
│   ├── EFileParser/           # 目录版本（推荐）
│   └── EFileParser_Single.exe # 单文件版本
├── install.bat                 # 安装程序
├── uninstall.bat              # 卸载程序
├── qt_app.py                  # Qt6主应用
├── efile_parser.py           # E文件解析器
└── 20260114/                 # 示例E文件
```

## 开发信息

- **GUI框架**: PyQt6 6.10.2
- **开发语言**: Python 3.13
- **打包工具**: PyInstaller 6.18.0
- **开发日期**: 2026年1月15日

## 文档

- `INSTALL_README.md` - 安装包详细说明
- `USAGE_GUIDE.md` - 使用指南
- `QT_VERSION_SUMMARY.md` - Qt版本项目总结

## 卸载

```bash
# 方法1：使用卸载程序
以管理员身份运行 uninstall.bat

# 方法2：手动删除
删除安装目录和桌面快捷方式
```

## 技术支持

如有问题，请参考 `INSTALL_READE.md` 中的常见问题部分。

---

**状态**: ✅ 完成并打包为EXE | **版本**: 1.0 | **日期**: 2026-01-15