import sys
import os
sys.path.insert(0, 'D:/001/eText')
from efile_parser import parse_efile
import time

print("=" * 60)
print("E文件解析工具 - 综合测试报告")
print("=" * 60)

# Test 1: tar.gz files
tar_base = 'D:/001/eText/102E文本数据202601'
tar_ok = 0
tar_err = 0
tar_total = 0

print(f"\n[1] 测试 tar.gz 文件目录: {tar_base}")

if os.path.isdir(tar_base):
    tar_files = [f for f in os.listdir(tar_base) if f.lower().endswith(('.tar.gz', '.tgz'))]
    tar_total = len(tar_files)
    print(f"    找到 {tar_total} 个 tar.gz 文件")
    
    for i, f in enumerate(sorted(tar_files)):
        path = os.path.join(tar_base, f)
        try:
            start_time = time.time()
            result = parse_efile(path)
            elapsed = time.time() - start_time
            sections = len(result.get('sections', []))
            dat_count = result.get('tar_info', {}).get('dat_count', 0) if result.get('tar_info') else 0
            status = 'OK' if sections > 0 or dat_count > 0 else 'WARN'
            print(f"    [{i+1}/{tar_total}] {f}")
            print(f"         sections={sections}, dats={dat_count}, time={elapsed:.3f}s, status={status}")
            tar_ok += 1
        except Exception as e:
            print(f"    [{i+1}/{tar_total}] {f} - 失败: {e}")
            tar_err += 1
    
    print(f"\n    tar.gz 测试结果: {tar_ok} 成功, {tar_err} 失败")
else:
    print(f"    错误: 目录不存在 - {tar_base}")

# Test 2: 102E2601 dat files
dat_base = 'D:/001/eText/102E2601'
dat_ok = 0
dat_err = 0
dat_total = 0

print(f"\n[2] 测试 .dat 文件目录: {dat_base}")

if os.path.isdir(dat_base):
    dat_files = [f for f in os.listdir(dat_base) if f.lower().endswith('.dat')]
    dat_total = len(dat_files)
    print(f"    找到 {dat_total} 个 .dat 文件")
    
    for i, f in enumerate(sorted(dat_files)):
        path = os.path.join(dat_base, f)
        try:
            result = parse_efile(path)
            sections = len(result.get('sections', []))
            # 只显示前5个和每1000个的进度
            if i < 5 or (i + 1) % 1000 == 0:
                print(f"    进度: {i+1}/{dat_total} - {f[:50]}")
            dat_ok += 1
        except Exception as e:
            print(f"    失败: {f} - {e}")
            dat_err += 1
    
    print(f"\n    102E2601 .dat 测试结果: {dat_ok} 成功, {dat_err} 失败")
else:
    print(f"    错误: 目录不存在 - {dat_base}")

# Test 3: 20260114 subdirectories
base_20260114 = 'D:/001/eText/20260114'
ok_20260114 = 0
err_20260114 = 0
total_20260114 = 0

print(f"\n[3] 测试 20260114 子目录: {base_20260114}")

if os.path.isdir(base_20260114):
    for root, dirs, files in os.walk(base_20260114):
        for f in files:
            if f.lower().endswith('.dat'):
                total_20260114 += 1
                path = os.path.join(root, f)
                try:
                    result = parse_efile(path)
                    sections = len(result.get('sections', []))
                    # 只显示前5个
                    if ok_20260114 < 5:
                        print(f"    [{ok_20260114+1}] {os.path.relpath(path, base_20260114)} - sections={sections}")
                    ok_20260114 += 1
                except Exception as e:
                    print(f"    失败: {os.path.relpath(path, base_20260114)} - {e}")
                    err_20260114 += 1
    
    print(f"\n    20260114 .dat 测试结果: {ok_20260114} 成功, {err_20260114} 失败 (总计 {total_20260114})")
else:
    print(f"    错误: 目录不存在 - {base_20260114}")

# Summary
print("\n" + "=" * 60)
print("测试总结")
print("=" * 60)
print(f"tar.gz 文件测试:     {tar_ok:3d} 成功, {tar_err:3d} 失败 (总计 {tar_total})")
print(f"102E2601 .dat 测试:  {dat_ok:5d} 成功, {dat_err:5d} 失败 (总计 {dat_total})")
print(f"20260114 .dat 测试:   {ok_20260114:5d} 成功, {err_20260114:5d} 失败 (总计 {total_20260114})")
print("=" * 60)
print("测试完成！")
print("=" * 60)

# Save log to file
log_path = 'D:/001/eText/test_results.log'
with open(log_path, 'w', encoding='utf-8') as log:
    log.write("=" * 60 + "\n")
    log.write("E文件解析工具 - 综合测试报告\n")
    log.write("=" * 60 + "\n\n")
    
    log.write(f"[1] tar.gz 文件测试目录: {tar_base}\n")
    log.write(f"    结果: {tar_ok} 成功, {tar_err} 失败 (总计 {tar_total})\n\n")
    
    log.write(f"[2] 102E2601 .dat 文件测试目录: {dat_base}\n")
    log.write(f"    结果: {dat_ok} 成功, {dat_err} 失败 (总计 {dat_total})\n\n")
    
    log.write(f"[3] 20260114 子目录测试: {base_20260114}\n")
    log.write(f"    结果: {ok_20260114} 成功, {err_20260114} 失败 (总计 {total_20260114})\n\n")
    
    log.write("=" * 60 + "\n")
    log.write("测试总结\n")
    log.write("=" * 60 + "\n")
    log.write(f"tar.gz 文件测试:     {tar_ok:3d} 成功, {tar_err:3d} 失败 (总计 {tar_total})\n")
    log.write(f"102E2601 .dat 测试:  {dat_ok:5d} 成功, {dat_err:5d} 失败 (总计 {dat_total})\n")
    log.write(f"20260114 .dat 测试:   {ok_20260114:5d} 成功, {err_20260114:5d} 失败 (总计 {total_20260114})\n")
    log.write("=" * 60 + "\n")

print(f"\n详细日志已保存到: {log_path}")
