#!/usr/bin/env python3
"""
PyInstaller build script for qt_app_v2_optimized_final.py
Creates a standalone Windows executable for the E文件解析工具
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any


class BuildConfig:
    """构建配置类"""
    def __init__(self, app_file: Path, output_name: str = "南网102-e文件解析工具"):
        self.app_file = app_file
        self.output_name = output_name
        self.icon_file = "spic_icon.ico"
        self.working_dir = app_file.parent.absolute()
        
        # PyInstaller 配置
        self.pyinstaller_options = {
            'name': output_name,
            'windowed': True,      # GUI application, no console
            'onefile': True,       # Single executable
            'clean': True,         # Clean PyInstaller cache
            'icon': self.icon_file,
            'hidden_imports': [
                'sqlite3',
                'winreg',
                'tarfile',
                'tempfile',
                'shutil',
                'datetime',
                'json',
                'PySide6',
                'PySide6.QtWidgets',
                'PySide6.QtCore',
                'PySide6.QtGui',
                'efile_parser_optimized',
                'db_utils_optimized',
                'efile_parser',
                'db_utils'
            ],
            'add_data': [
                (self.icon_file, '.'),
                ('spic_logo.png', '.'),
                ('eparser.db', '.'),
            ],
            'excludes': [
                'tkinter',
                'matplotlib',
                'numpy',
                'scipy',
                'pandas',
                'jupyter',
                'test',
                'unittest'
            ],
            'runtime_hooks': [],
            'key': None,  # 可选：用于加密字节码
        }
    
    def get_build_command(self) -> List[str]:
        """生成构建命令"""
        cmd = [sys.executable, "-m", "PyInstaller"]
        
        # 基本选项
        cmd.extend(["--name", self.pyinstaller_options['name']])
        if self.pyinstaller_options['windowed']:
            cmd.append("--windowed")
        if self.pyinstaller_options['onefile']:
            cmd.append("--onefile")
        if self.pyinstaller_options['clean']:
            cmd.append("--clean")
        if self.pyinstaller_options['icon']:
            cmd.extend(["--icon", self.pyinstaller_options['icon']])
        
        # 隐藏导入
        for module in self.pyinstaller_options['hidden_imports']:
            cmd.extend(["--hidden-import", module])
        
        # 添加数据文件
        for src, dest in self.pyinstaller_options['add_data']:
            cmd.extend(["--add-data", f"{src};{dest}"])
        
        # 排除模块
        for module in self.pyinstaller_options['excludes']:
            cmd.extend(["--exclude-module", module])
        
        # 运行时钩子
        for hook in self.pyinstaller_options['runtime_hooks']:
            cmd.extend(["--runtime-hook", hook])
        
        # 密钥
        if self.pyinstaller_options['key']:
            cmd.extend(["--key", self.pyinstaller_options['key']])
        
        # 应用文件
        cmd.append(str(self.app_file))
        
        return cmd


class BuildManager:
    """构建管理器"""
    def __init__(self, config: BuildConfig):
        self.config = config
        self.build_log = []
    
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}"
        self.build_log.append(log_entry)
        print(log_entry)
    
    def check_prerequisites(self) -> bool:
        """检查构建前提条件"""
        self.log("检查构建前提条件...")
        
        # 检查应用文件是否存在
        if not self.config.app_file.exists():
            self.log(f"错误: {self.config.app_file} 不存在!", "ERROR")
            return False
        
        # 检查图标文件
        icon_path = self.config.working_dir / self.config.icon_file
        if not icon_path.exists():
            self.log(f"警告: 图标文件 {icon_path} 不存在，将使用默认图标", "WARNING")
            self.config.pyinstaller_options['icon'] = None
        
        # 检查 PyInstaller 是否安装
        try:
            result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                                  capture_output=True, text=True, check=True)
            self.log(f"PyInstaller 版本: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            self.log("错误: PyInstaller 未安装，请运行 'pip install pyinstaller'", "ERROR")
            return False
        
        # 检查 PySide6 是否安装
        try:
            import PySide6
            self.log(f"PySide6 版本: {PySide6.__version__}")
        except ImportError:
            self.log("错误: PySide6 未安装，请运行 'pip install PySide6'", "ERROR")
            return False
        
        self.log("✅ 前提条件检查通过")
        return True
    
    def create_build_info(self) -> Dict[str, Any]:
        """创建构建信息"""
        return {
            'build_time': datetime.now().isoformat(),
            'app_file': str(self.config.app_file),
            'output_name': self.config.output_name,
            'pyinstaller_version': self.get_pyinstaller_version(),
            'python_version': sys.version,
            'platform': sys.platform,
            'build_options': self.config.pyinstaller_options
        }
    
    def get_pyinstaller_version(self) -> str:
        """获取 PyInstaller 版本"""
        try:
            result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def run_build(self) -> bool:
        """执行构建过程"""
        self.log("=" * 60)
        self.log(f"开始构建: {self.config.output_name}")
        self.log("=" * 60)
        
        # 检查前提条件
        if not self.check_prerequisites():
            return False
        
        # 生成构建命令
        build_cmd = self.config.get_build_command()
        self.log(f"构建命令: {' '.join(build_cmd)}")
        self.log("-" * 50)
        
        # 执行构建
        try:
            self.log("开始执行构建命令...")
            result = subprocess.run(
                build_cmd, 
                cwd=self.config.working_dir, 
                check=False,
                capture_output=False,  # 实时显示输出
                text=True
            )
            
            if result.returncode == 0:
                self.log("✅ 构建成功完成!")
                self.log_build_summary()
                return True
            else:
                self.log(f"❌ 构建失败，返回码: {result.returncode}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 构建过程中发生异常: {e}", "ERROR")
            return False
    
    def log_build_summary(self):
        """记录构建摘要"""
        self.log("=" * 60)
        self.log("构建摘要:")
        self.log("=" * 60)
        
        # 查找生成的可执行文件
        dist_dir = self.config.working_dir / "dist"
        if dist_dir.exists():
            exe_files = list(dist_dir.glob("*.exe"))
            if exe_files:
                exe_file = exe_files[0]
                file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
                self.log(f"可执行文件: {exe_file.name}")
                self.log(f"文件大小: {file_size:.2f} MB")
                self.log(f"完整路径: {exe_file.absolute()}")
            else:
                self.log("⚠️ 未找到生成的可执行文件")
        else:
            self.log("⚠️ dist 目录不存在")
        
        # 构建信息
        build_info = self.create_build_info()
        self.log(f"构建时间: {build_info['build_time']}")
        self.log(f"Python 版本: {build_info['python_version'].split()[0]}")
        self.log(f"平台: {build_info['platform']}")
        self.log(f"PyInstaller 版本: {build_info['pyinstaller_version']}")
        
        self.log("=" * 60)
    
    def save_build_log(self, filename: str = "build_log.txt"):
        """保存构建日志到文件"""
        log_file = self.config.working_dir / filename
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.build_log))
            self.log(f"构建日志已保存到: {log_file}")
        except Exception as e:
            self.log(f"保存构建日志失败: {e}", "ERROR")


def main():
    parser = argparse.ArgumentParser(description='构建南网102-e文件解析工具')
    parser.add_argument('--app', '-a', type=str, default='qt_app_v2_optimized_final.py',
                       help='要构建的应用文件 (默认: qt_app_v2_optimized_final.py)')
    parser.add_argument('--name', '-n', type=str, default='南网102-e文件解析工具',
                       help='输出的可执行文件名 (默认: 南网102-e文件解析工具)')
    parser.add_argument('--no-clean', action='store_true',
                       help='不清除 PyInstaller 缓存')
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细输出')
    
    args = parser.parse_args()
    
    # 创建配置
    app_file = Path(args.app)
    config = BuildConfig(app_file, args.name)
    
    # 应用命令行选项
    if args.no_clean:
        config.pyinstaller_options['clean'] = False
    if args.debug:
        config.pyinstaller_options['windowed'] = False  # 调试模式显示控制台
    
    # 创建构建管理器
    build_manager = BuildManager(config)
    
    # 执行构建
    success = build_manager.run_build()
    
    # 保存日志
    build_manager.save_build_log()
    
    # 退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    from datetime import datetime
    main()