#!/usr/bin/env python3
"""
创建 E文件解析工具 安装包
Create E-file Parser Tool Installation Package
"""

import os
import sys
import zipfile
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
import subprocess


class PackageBuilder:
    """安装包构建器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.absolute()
        self.package_name = "E文件解析工具_优化版"
        self.version = "2.1.3"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 要包含的文件列表
        self.files_to_include = [
            # 核心应用文件
            "qt_app_v2_optimized_final.py",
            "efile_parser_optimized.py", 
            "db_utils_optimized.py",
            
            # 资源文件
            "spic_icon.ico",
            "spic_logo.png",
            
            # 依赖文件
            "requirements_optimized.txt",
            
            # 构建文件
            "build_qt_app_v2_optimized.py",
            
            # 文档文件
            "README.md",
            "南方电网新能源数据上送规范 V3.3修订版（2022.2月）.pdf",
        ]
        
        # 可选文件（如果存在则包含）
        self.optional_files = [
            "README_SPIC.md",
            "国家电投LOGO矢量文件 - 副本.ai",
        ]
        
        # 目录结构
        self.package_structure = {
            "E文件解析工具_优化版": {
                "源代码": [
                    "qt_app_v2_optimized_final.py",
                    "efile_parser_optimized.py",
                    "db_utils_optimized.py",
                    "requirements_optimized.txt",
                    "build_qt_app_v2_optimized.py",
                ],
                "资源文件": [
                    "spic_icon.ico",
                    "spic_logo.png",
                ],
                "文档": [
                    "README.md",
                    "南方电网新能源数据上送规范 V3.3修订版（2022.2月）.pdf",
                ],
                "示例数据": [],  # 稍后添加
            }
        }
    
    def check_prerequisites(self):
        """检查构建前提条件"""
        print("🔍 检查构建前提条件...")
        
        missing_files = []
        for file_path in self.files_to_include:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ 缺少以下文件: {', '.join(missing_files)}")
            return False
        
        print("✅ 前提条件检查通过")
        return True
    
    def collect_sample_data(self):
        """收集示例数据"""
        sample_data_dir = self.project_root / "102E2601"
        sample_files = []
        
        if sample_data_dir.exists():
            # 收集最近的几个 .dat 文件作为示例
            dat_files = list(sample_data_dir.glob("*.dat"))
            if dat_files:
                # 取最新的5个文件
                dat_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                sample_files = dat_files[:5]
                print(f"📁 找到 {len(sample_files)} 个示例数据文件")
        
        return sample_files
    
    def create_package_structure(self, temp_dir):
        """创建安装包目录结构"""
        print("🏗️ 创建安装包目录结构...")
        
        package_root = temp_dir / self.package_name
        package_root.mkdir(parents=True, exist_ok=True)
        
        # 创建目录结构
        for dir_name, files in self.package_structure.items():
            dir_path = package_root / dir_name
            dir_path.mkdir(exist_ok=True)
            
            # 复制文件
            for file_name in files:
                src_file = self.project_root / file_name
                dst_file = dir_path / file_name
                if src_file.exists():
                    shutil.copy2(src_file, dst_file)
                    print(f"  ✅ 复制: {file_name}")
        
        # 添加示例数据
        sample_files = self.collect_sample_data()
        if sample_files:
            sample_dir = package_root / "示例数据"
            sample_dir.mkdir(exist_ok=True)
            
            for sample_file in sample_files:
                dst_file = sample_dir / sample_file.name
                shutil.copy2(sample_file, dst_file)
                print(f"  ✅ 复制示例数据: {sample_file.name}")
        
        # 创建安装说明
        self.create_installation_guide(package_root)
        
        # 创建快速启动脚本
        self.create_quick_start_script(package_root)
        
        return package_root
    
    def create_installation_guide(self, package_root):
        """创建安装说明文档"""
        guide_content = f"""# E文件解析工具 安装指南

## 版本信息
- 版本: {self.version}
- 构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 构建者: 自动构建工具

## 安装步骤

### 1. 环境准备
确保已安装 Python 3.8 或更高版本

### 2. 安装依赖
在命令行中执行：
```bash
cd "E文件解析工具_优化版\\源代码"
pip install -r requirements_optimized.txt
```

### 3. 运行应用
```bash
cd "E文件解析工具_优化版\\源代码"
python qt_app_v2_optimized_final.py
```

### 4. 打包为可执行文件（可选）
```bash
cd "E文件解析工具_优化版\\源代码"
python build_qt_app_v2_optimized.py
```

## 文件说明

### 源代码目录
- `qt_app_v2_optimized_final.py` - 主应用程序
- `efile_parser_optimized.py` - E文件解析器
- `db_utils_optimized.py` - 数据库工具
- `requirements_optimized.txt` - 依赖列表
- `build_qt_app_v2_optimized.py` - 构建脚本

### 资源文件目录
- `spic_icon.ico` - 应用图标
- `spic_logo.png` - SPIC Logo

### 文档目录
- `README.md` - 项目说明
- `南方电网新能源数据上送规范 V3.3修订版（2022.2月）.pdf` - 规范文档

### 示例数据目录
包含用于测试的示例 E文件

## 技术特性

### 优化特性
- ✅ 性能优化 - 使用上下文管理器和类型注解
- ✅ 错误处理 - 完善的异常处理机制
- ✅ 代码结构 - 模块化设计，易于维护
- ✅ 用户体验 - 改进的界面响应和提示

### 支持的文件格式
- 单个 .dat 文件
- .tar.gz 压缩包
- .lbx 压缩包（ZIP格式）

### 数据库功能
- SQLite 数据库存储
- 解析结果查询和管理
- 统计信息查看

## 联系方式
- 开发者: 陈丰
- 电话: 0871-65666603
- 单位: 国家电投云南国际 昆明生产运营中心

## 版权信息
© 2024 国家电投云南国际 版权所有
"""
        
        guide_file = package_root / "安装指南.md"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        print("  ✅ 创建安装指南: 安装指南.md")
    
    def create_quick_start_script(self, package_root):
        """创建快速启动脚本"""
        script_content = '''@echo off
echo.
echo ================================
echo   E文件解析工具 快速启动
echo ================================
echo.
echo 1. 运行源代码版本
echo 2. 构建可执行文件
echo 3. 查看安装指南
echo 4. 退出
echo.
set /p choice=请选择操作 (1-4): 

if "%choice%"=="1" goto run_source
if "%choice%"=="2" goto build_exe
if "%choice%"=="3" goto view_guide
if "%choice%"=="4" goto exit_script

:run_source
echo.
echo 正在启动源代码版本...
cd "源代码"
python qt_app_v2_optimized_final.py
goto end

:build_exe
echo.
echo 正在构建可执行文件...
cd "源代码"
python build_qt_app_v2_optimized.py
echo.
echo 构建完成！可执行文件在 dist 目录中。
pause
goto end

:view_guide
echo.
echo 正在打开安装指南...
start "" "安装指南.md"
goto end

:exit_script
echo.
echo 感谢使用！
goto end

:end
echo.
pause
'''
        
        script_file = package_root / "快速启动.bat"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print("  ✅ 创建快速启动脚本: 快速启动.bat")
    
    def create_zip_package(self, package_root):
        """创建 ZIP 安装包"""
        zip_filename = f"{self.package_name}_v{self.version}_{self.timestamp}.zip"
        zip_path = self.project_root / zip_filename
        
        print(f"📦 创建 ZIP 安装包: {zip_filename}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_root):
                # 计算相对路径
                rel_path = Path(root).relative_to(package_root)
                
                # 添加目录
                if rel_path != Path('.'):
                    zipf.write(root, rel_path)
                
                # 添加文件
                for file in files:
                    file_path = Path(root) / file
                    arc_path = rel_path / file
                    zipf.write(file_path, arc_path)
                    print(f"  📁 添加: {arc_path}")
        
        return zip_path
    
    def build_package(self):
        """构建安装包"""
        print("=" * 60)
        print("🚀 开始构建 E文件解析工具 安装包")
        print("=" * 60)
        print(f"📦 版本: {self.version}")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # 检查前提条件
        if not self.check_prerequisites():
            print("❌ 构建失败：前提条件不满足")
            return False
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # 创建包结构
                package_root = self.create_package_structure(temp_path)
                
                # 创建 ZIP 包
                zip_path = self.create_zip_package(package_root)
                
                # 显示构建信息
                self.show_build_summary(zip_path)
                
                print("✅ 安装包构建成功！")
                return True
                
            except Exception as e:
                print(f"❌ 构建过程中发生错误: {e}")
                return False
    
    def show_build_summary(self, zip_path):
        """显示构建摘要"""
        print("\n" + "=" * 60)
        print("📊 构建摘要")
        print("=" * 60)
        
        # 文件大小
        file_size = zip_path.stat().st_size / (1024 * 1024)
        print(f"📦 安装包文件: {zip_path.name}")
        print(f"📏 文件大小: {file_size:.2f} MB")
        print(f"📁 完整路径: {zip_path}")
        
        # 包含的文件统计
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            file_count = len(zipf.namelist())
            print(f"📄 包含文件数: {file_count}")
        
        print(f"⏰ 构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)


def main():
    """主函数"""
    try:
        import tempfile
    except ImportError:
        print("❌ 错误: 缺少 tempfile 模块")
        return 1
    
    # 创建构建器并构建包
    builder = PackageBuilder()
    success = builder.build_package()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())