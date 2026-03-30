#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量导入E文件到数据库工具
国家电投昆明生产运营中心 版权所有
作者: 陈丰 联系电话: 0871-65666603
"""

import os
import sys
import tarfile
import tempfile
import shutil
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from efile_parser import parse_efile
from db_utils_v33_final import init_db, save_result

def extract_tar_gz(tar_path, extract_to):
    """解压tar.gz文件到指定目录"""
    try:
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.extractall(extract_to)
        return True
    except Exception as e:
        print(f"解压失败 {tar_path}: {e}")
        return False

def process_directory(directory_path, recursive=True):
    """处理目录中的所有E文件"""
    directory = Path(directory_path)
    if not directory.exists():
        print(f"目录不存在: {directory_path}")
        return
    
    print(f"开始处理目录: {directory_path}")
    
    # 统计信息
    total_files = 0
    processed_files = 0
    failed_files = 0
    
    # 收集所有文件
    files_to_process = []
    
    if recursive:
        # 递归搜索所有.dat文件
        for file_path in directory.rglob("*.dat"):
            files_to_process.append(file_path)
    else:
        # 只搜索当前目录
        for file_path in directory.glob("*.dat"):
            files_to_process.append(file_path)
    
    # 处理.tar.gz文件
    for file_path in directory.glob("*.tar.gz"):
        files_to_process.append(file_path)
    
    total_files = len(files_to_process)
    print(f"找到 {total_files} 个文件需要处理")
    
    # 处理每个文件
    for i, file_path in enumerate(files_to_process, 1):
        print(f"\n[{i}/{total_files}] 处理文件: {file_path}")
        
        try:
            if file_path.suffix == '.tar.gz':
                # 处理tar.gz文件
                with tempfile.TemporaryDirectory() as temp_dir:
                    if extract_tar_gz(file_path, temp_dir):
                        # 递归处理解压后的文件
                        process_directory(temp_dir, recursive=False)
                        processed_files += 1
                        print(f"  ✓ tar.gz文件处理完成")
                    else:
                        failed_files += 1
                        print(f"  ✗ tar.gz文件解压失败")
            else:
                # 处理单个.dat文件
                result = parse_efile(str(file_path))
                save_result(result)
                processed_files += 1
                print(f"  ✓ 文件解析并保存成功")
                
        except Exception as e:
            failed_files += 1
            print(f"  ✗ 处理失败: {e}")
    
    print(f"\n处理完成!")
    print(f"总计: {total_files} 个文件")
    print(f"成功: {processed_files} 个文件")
    print(f"失败: {failed_files} 个文件")

def main():
    """主函数"""
    # 初始化数据库
    print("初始化数据库...")
    init_db()
    
    # 处理指定目录
    directories = [
        r"D:\001\eText\102E2601",
        r"D:\001\eText\102E文本数据202601", 
        r"D:\001\eText\20260114"
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            process_directory(directory, recursive=True)
        else:
            print(f"目录不存在，跳过: {directory}")
    
    print("\n所有目录处理完成!")

if __name__ == "__main__":
    main()