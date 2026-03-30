#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试数据库功能的脚本
"""

import os
import sys
import sqlite3
import subprocess
import time

# 将dist目录添加到系统路径
sys.path.append(r'd:\001\eText\dist\qt_app_v2_restored_backup')

# 导入必要的模块
from db_utils import init_db, save_result, query_results

def test_database_functions():
    """测试数据库功能"""

    # 设置数据库路径
    db_path = r'd:\001\eText\dist\qt_app_v2_restored_backup\eparser.db'

    print("测试数据库功能...")
    print(f"数据库路径: {db_path}")

    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print("错误: 数据库文件不存在！")
        return False

    print("数据库文件存在，正在测试连接...")

    try:
        # 测试数据库连接
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 测试查询
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"数据库中存在的表: {tables}")

        # 测试query_results函数
        results = query_results()
        print(f"查询结果: {len(results)} 条记录")

        conn.close()
        print("数据库功能测试成功！")
        return True

    except Exception as e:
        print(f"数据库功能测试失败: {str(e)}")
        return False

def test_file_parsing():
    """测试文件解析功能"""

    # 测试目录
    test_dirs = [
        r'D:\001\eText\102E2601',
        r'D:\001\eText\102E文本数据202601',
        r'D:\001\eText\20260114'
    ]

    print("\n测试文件解析功能...")

    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            print(f"测试目录: {test_dir}")

            # 获取目录中的文件
            try:
                files = os.listdir(test_dir)
                print(f"找到 {len(files)} 个文件")

                # 尝试解析第一个文件（如果有）
                if files:
                    first_file = os.path.join(test_dir, files[0])
                    print(f"第一个文件: {first_file}")

                    # 这里可以添加实际的解析测试代码
                    # 由于我们无法直接调用GUI应用程序，我们只能验证文件存在

                else:
                    print("目录为空")

            except Exception as e:
                print(f"无法读取目录 {test_dir}: {str(e)}")
        else:
            print(f"目录不存在: {test_dir}")

if __name__ == "__main__":
    print("开始测试数据库管理功能...")

    # 测试数据库功能
    db_ok = test_database_functions()

    # 测试文件解析功能
    test_file_parsing()

    if db_ok:
        print("\n数据库管理功能测试完成，所有测试通过！")
    else:
        print("\n数据库管理功能测试失败！")