# -*- coding: utf-8 -*-
"""
全面测试脚本 - 测试所有目录下的文件
"""

import os
import sys
from datetime import datetime

# 导入解析模块
from efile_parser import parse_efile

# 测试目录
TEST_DIRS = {
    "102E文本数据202601": r"D:\001\eText\102E文本数据202601",
    "102E2601": r"D:\001\eText\102E2601",
    "20260114": r"D:\001\eText\20260114"
}

def get_files_by_extension(directory, extensions):
    """获取目录下指定扩展名的文件"""
    files = []
    if not os.path.exists(directory):
        print(f"目录不存在: {directory}")
        return files
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            for ext in extensions:
                if filename.endswith(ext):
                    files.append(filepath)
                    break
    
    return sorted(files)

def get_files_recursive(directory, extensions):
    """递归获取目录下所有文件"""
    files = []
    if not os.path.exists(directory):
        print(f"目录不存在: {directory}")
        return files
    
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            for ext in extensions:
                if filename.endswith(ext):
                    files.append(filepath)
                    break
    
    return sorted(files)

def test_file(filepath):
    """测试单个文件"""
    try:
        result = parse_efile(filepath)
        return True, result
    except Exception as e:
        return False, str(e)

def test_directory(name, directory, extensions, recursive=False):
    """测试目录"""
    print(f"\n{'='*60}")
    print(f"测试目录: {name}")
    print(f"路径: {directory}")
    print(f"{'='*60}")
    
    if recursive:
        files = get_files_recursive(directory, extensions)
    else:
        files = get_files_by_extension(directory, extensions)
    
    if not files:
        print(f"未找到任何文件 (扩展名: {extensions})")
        return 0, 0
    
    total = len(files)
    success = 0
    failed = 0
    
    print(f"共找到 {total} 个文件")
    print(f"开始测试...\n")
    
    for i, filepath in enumerate(files, 1):
        print(f"[{i}/{total}] 测试文件: {os.path.basename(filepath)}", end=" ... ")
        
        ok, result = test_file(filepath)
        
        if ok:
            success += 1
            # 显示简要信息
            sections_count = len(result.get("sections", []))
            print(f"成功 (数据段: {sections_count})")
        else:
            failed += 1
            error_msg = result if isinstance(result, str) else "未知错误"
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            print(f"失败: {error_msg}")
    
    print(f"\n测试完成: 成功 {success}/{total}, 失败 {failed}/{total}")
    return success, failed

def main():
    """主函数"""
    print("="*60)
    print("e文件全面测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    total_success = 0
    total_failed = 0
    
    # 1. 测试 102E文本数据202601 下的 .tar.gz 文件
    print("\n[1/3] 测试 tar.gz 文件...")
    success, failed = test_directory(
        "102E文本数据202601",
        TEST_DIRS["102E文本数据202601"],
        [".tar.gz"]
    )
    total_success += success
    total_failed += failed
    
    # 2. 测试 102E2601 下的 .dat 文件
    print("\n[2/3] 测试 102E2601 目录的 .dat 文件...")
    success, failed = test_directory(
        "102E2601",
        TEST_DIRS["102E2601"],
        [".dat"]
    )
    total_success += success
    total_failed += failed
    
    # 3. 测试 20260114 下的所有 .dat 文件
    print("\n[3/3] 测试 20260114 目录的 .dat 文件...")
    success, failed = test_directory(
        "20260114",
        TEST_DIRS["20260114"],
        [".dat"],
        recursive=True
    )
    total_success += success
    total_failed += failed
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总计: 成功 {total_success}, 失败 {total_failed}")
    print(f"总计: {total_success + total_failed} 个文件")
    print("="*60)

if __name__ == "__main__":
    main()
