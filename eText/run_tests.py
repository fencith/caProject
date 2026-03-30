import sys
import os
sys.path.insert(0, 'D:/001/eText')
from efile_parser import parse_efile
import time

print("Starting comprehensive tests...")

# Test 1: tar.gz files
tar_base = 'D:/001/eText/102E文本数据202601'
if os.path.isdir(tar_base):
    tar_files = [f for f in os.listdir(tar_base) if f.lower().endswith(('.tar.gz', '.tgz'))]
    print(f'Found {len(tar_files)} tar.gz files')
    
    tar_ok = 0
    tar_err = 0
    
    for i, f in enumerate(sorted(tar_files)):
        path = os.path.join(tar_base, f)
        try:
            result = parse_efile(path)
            sections = len(result.get('sections', []))
            dat_count = result.get('tar_info', {}).get('dat_count', 0)
            print(f'TAR {i+1}/{len(tar_files)}: {f} - sections={sections}, dats={dat_count}')
            tar_ok += 1
        except Exception as e:
            print(f'TAR FAIL: {f} - {e}')
            tar_err += 1
    
    print(f'Tar.gz test: {tar_ok} OK, {tar_err} ERR')
else:
    print(f'Tar directory not found: {tar_base}')

# Test 2: 102E2601 dat files
dat_base = 'D:/001/eText/102E2601'
if os.path.isdir(dat_base):
    dat_files = [f for f in os.listdir(dat_base) if f.lower().endswith('.dat')]
    print(f'Found {len(dat_files)} dat files in 102E2601')
    
    dat_ok = 0
    dat_err = 0
    
    for i, f in enumerate(sorted(dat_files)):
        path = os.path.join(dat_base, f)
        try:
            result = parse_efile(path)
            sections = len(result.get('sections', []))
            if i < 5 or i % 1000 == 0:
                print(f'DAT {i+1}/{len(dat_files)}: {f} - sections={sections}')
            dat_ok += 1
        except Exception as e:
            print(f'DAT FAIL: {f} - {e}')
            dat_err += 1
    
    print(f'Dat 102E2601 test: {dat_ok} OK, {dat_err} ERR')
else:
    print(f'Dat directory not found: {dat_base}')

# Test 3: 20260114 subdirectories
base_20260114 = 'D:/001/eText/20260114'
if os.path.isdir(base_20260114):
    dat_count_20260114 = 0
    ok_20260114 = 0
    err_20260114 = 0
    
    for root, dirs, files in os.walk(base_20260114):
        for f in files:
            if f.lower().endswith('.dat'):
                dat_count_20260114 += 1
                path = os.path.join(root, f)
                try:
                    result = parse_efile(path)
                    sections = len(result.get('sections', []))
                    if ok_20260114 < 5 or ok_20260114 % 1000 == 0:
                        print(f'20260114 DAT {ok_20260114}: {os.path.relpath(path, base_20260114)} - sections={sections}')
                    ok_20260114 += 1
                except Exception as e:
                    print(f'20260114 FAIL: {os.path.relpath(path, base_20260114)} - {e}')
                    err_20260114 += 1
    
    print(f'Dat 20260114 test: {ok_20260114} OK, {err_20260114} ERR (total {dat_count_20260114})')
else:
    print(f'Directory not found: {base_20260114}')

print('\nTest Summary:')
tar_ok = locals().get('tar_ok', 0)
tar_err = locals().get('tar_err', 0)
dat_ok = locals().get('dat_ok', 0)
dat_err = locals().get('dat_err', 0)
ok_20260114 = locals().get('ok_20260114', 0)
err_20260114 = locals().get('err_20260114', 0)

print(f'Tar.gz: {tar_ok} OK, {tar_err} ERR')
print(f'Dat 102E2601: {dat_ok} OK, {dat_err} ERR')
print(f'Dat 20260114: {ok_20260114} OK, {err_20260114} ERR')
