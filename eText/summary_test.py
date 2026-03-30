# -*- coding: utf-8 -*-
"""
总结测试结果 - 从已完成的测试中获取总结信息
"""

import os
from efile_parser import parse_efile

def count_files_in_dir(directory, extensions):
    """统计目录中的文件数量"""
    count = 0
    if not os.path.exists(directory):
        return count
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            for ext in extensions:
                if filename.endswith(ext):
                    count += 1
                    break
    
    return count

def count_files_recursive(directory, extensions):
    """递归统计目录中的文件数量"""
    count = 0
    if not os.path.exists(directory):
        return count
    
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            for ext in extensions:
                if filename.endswith(ext):
                    count += 1
                    break
    
    return count

def main():
    print("="*60)
    print("文件统计总结")
    print("="*60)
    
    # 1. 统计 102E文本数据202601 下的 .tar.gz 文件
    tar_gz_dir = r"D:\001\eText\102E文本数据202601"
    tar_gz_count = count_files_in_dir(tar_gz_dir, [".tar.gz"])
    print(f"\n[1] 102E文本数据202601:")
    print(f"    .tar.gz 文件数量: {tar_gz_count}")
    
    # 2. 统计 102E2601 下的 .dat 文件
    dat_dir = r"D:\001\eText\102E2601"
    dat_count = count_files_in_dir(dat_dir, [".dat"])
    print(f"\n[2] 102E2601:")
    print(f"    .dat 文件数量: {dat_count}")
    
    # 3. 统计 20260114 下的所有 .dat 文件
    subdirs_dir = r"D:\001\eText\20260114"
    subdir_dat_count = count_files_recursive(subdirs_dir, [".dat"])
    print(f"\n[3] 20260114 (递归):")
    print(f"    .dat 文件数量: {subdir_dat_count}")
    
    total = tar_gz_count + dat_count + subdir_dat_count
    print(f"\n总计: {total} 个文件")
    print("="*60)
    
    # 测试几个文件样本
    print("\n测试文件样本...")
    
    sample_files = [
        r"D:\001\eText\102E文本数据202601\DZL_DQYC_202601.tar.gz",
        r"D:\001\eText\102E2601\FD_YN.DeZLDC_DQYC_20260101_080000.dat",
        r"D:\001\eText\20260114\DQYC\FD_GD.GDZJYHHB_DQYC_20260114_090000.dat"
    ]
    
    for filepath in sample_files:
        if os.path.exists(filepath):
            print(f"\n  测试: {os.path.basename(filepath)}", end=" ... ")
            try:
                result = parse_efile(filepath)
                sections_count = len(result.get("sections", []))
                print(f"成功 (数据段: {sections_count})")
            except Exception as e:
                print(f"失败: {str(e)[:50]}")
        else:
            print(f"\n  文件不存在: {filepath}")

if __name__ == "__main__":
    main()
