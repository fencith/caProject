# -*- coding: utf-8 -*-
"""
Lite版快速验证脚本
验证eFileParser_lite.exe是否能正常启动
"""

import os
import sys
import subprocess
import time

def main():
    print("="*70)
    print("eFileParser Lite版 - 快速验证")
    print("="*70)
    print()

    exe_path = r"D:\001\eText\dist\eFileParser_lite.exe"

    if not os.path.exists(exe_path):
        print(f"[ERROR] Lite版exe未找到: {exe_path}")
        print()
        print("请先运行打包命令生成lite版exe:")
        print("  cd D:\\001\\eText")
        print("  python -m PyInstaller --onefile --windowed --name=\"eFileParser_lite\" \\")
        print("    --add-data=\"D:\\001\\eTextDTA\\logo\\spic-logo.svg;.\" --add-data=\"efile_parser.py;.\" \\")
        print("    --add-data=\"db_utils.py;.\" \\")
        print("    --hidden-import=\"PySide6.QtWidgets\" \\")
        print("    --hidden-import=\"PySide6.QtCore\" \\")
        print("    --hidden-import=\"PySide6.QtGui\" \\")
        print("    --exclude-module=\"PySide6.QtNetwork\" \\")
        print("    --exclude-module=\"PySide6.QtNetworkAuth\" \\")
        print("    --exclude-module=\"PySide6.QtWebEngine\" \\")
        print("    --exclude-module=\"PySide6.QtWebEngineWidgets\" \\")
        print("    qt_app_v2.py")
        return 1

    file_size = os.path.getsize(exe_path)
    file_size_mb = file_size / (1024 * 1024)

    print(f"[OK] Lite版exe已找到")
    print(f"     文件路径: {exe_path}")
    print(f"     文件大小: {file_size_mb:.2f} MB")
    print()

    # 启动exe
    print("[INFO] 正在启动Lite版exe...")
    try:
        proc = subprocess.Popen(
            [exe_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("[OK] exe进程已启动")
        print(f"     进程ID: {proc.pid}")
        print()

        # 等待5秒
        print("[INFO] 等待5秒以确认应用启动...")
        time.sleep(5)
        print()

        # 检查进程状态
        return_code = proc.poll()

        if return_code is None:
            print("="*70)
            print("验证结果: 成功 [OK]")
            print("="*70)
            print()
            print("Lite版exe启动成功！")
            print()
            print("应用程序正在运行中。")
            print("请手动测试以下功能:")
            print("  1. 文件选择功能")
            print("  2. 文件解析功能")
            print("  3. 数据查看功能")
            print("  4. 导出报告功能")
            print()
            print("完成后请关闭应用程序窗口。")
            print()
            return 0
        else:
            print("="*70)
            print("验证结果: 失败 [FAIL]")
            print("="*70)
            print()
            print(f"exe已退出，返回码: {return_code}")
            print()
            print("可能的原因:")
            print("  1. 缺少必要的运行时库")
            print("  2. 文件权限问题")
            print("  3. 杀毒软件阻止")
            print()
            print("建议:")
            print("  1. 以管理员身份运行")
            print("  2. 暂时禁用杀毒软件")
            print("  3. 从命令行运行查看错误信息:")
            print(f"     {exe_path}")
            print()
            return 1

    except Exception as e:
        print(f"[ERROR] 启动exe失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    success = main()
    print()
    if success == 0:
        print("验证完成！")
    else:
        print("验证失败！")
    sys.exit(success)
