#!/usr/bin/env python3
"""
Clear Windows icon cache to ensure new application icon displays properly
"""
import os
import subprocess
import shutil
import time

def clear_windows_icon_cache():
    """Clear Windows icon cache"""
    try:
        print("🧹 清除 Windows 图标缓存...")

        # Stop Windows Explorer
        print("1. 停止 Windows 资源管理器...")
        subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], check=True)
        time.sleep(2)

        # Clear icon cache files
        print("2. 清除图标缓存文件...")

        # Get user profile directory
        user_profile = os.environ.get('USERPROFILE', os.path.expanduser('~'))

        # Icon cache files to delete
        icon_cache_files = [
            os.path.join(user_profile, 'AppData\\Local\\Microsoft\\Windows\\Explorer\\iconcache_*.db'),
            os.path.join(user_profile, 'AppData\\Local\\Microsoft\\Windows\\Explorer\\thumbcache_*.db'),
        ]

        # Delete icon cache files
        for pattern in icon_cache_files:
            try:
                # Use PowerShell to delete files with wildcard
                subprocess.run(['powershell', '-Command', f'Remove-Item -Path "{pattern}" -Force'], check=True)
                print(f"   ✅ 已删除: {pattern}")
            except subprocess.CalledProcessError:
                print(f"   ⚠️  文件不存在或无法删除: {pattern}")

        # Restart Windows Explorer
        print("3. 重新启动 Windows 资源管理器...")
        subprocess.run(['start', 'explorer.exe'], shell=True)
        time.sleep(3)

        print("✅ Windows 图标缓存已清除完成！")
        print("💡 请重新启动应用程序以查看新的图标。")

        return True

    except Exception as e:
        print(f"❌ 清除图标缓存失败: {e}")
        return False

def main():
    """Main function"""
    print("🔄 Windows 图标缓存清理工具")
    print("=" * 50)

    success = clear_windows_icon_cache()

    if success:
        print("\n🎉 操作完成！")
        print("请尝试重新启动 E文件解析工具Ver2.1.exe 查看新图标。")
    else:
        print("\n❌ 操作失败！")
        print("请手动重启计算机或尝试其他方法。")

if __name__ == "__main__":
    main()