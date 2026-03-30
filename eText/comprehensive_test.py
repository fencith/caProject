#!/usr/bin/env python3
"""
Comprehensive individual file testing script
Tests each tar.gz file in 102E文本数据2026.01/, each dat file in 102E2601/, and each dat file in 20260114/ subdirectories
"""

import os
import json
import logging
from datetime import datetime
from qt_app import EFileParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_tar_gz_files():
    """Test each tar.gz file individually"""
    print("="*80)
    print("TESTING TAR.GZ FILES IN 102E文本数据2026.01/")
    print("="*80)

    results = {}
    tar_gz_dir = os.path.join(os.getcwd(), '102E文本数据2026.01')

    if not os.path.exists(tar_gz_dir):
        print(f"Directory not found: {tar_gz_dir}")
        return results

    tar_gz_files = [f for f in os.listdir(tar_gz_dir) if f.endswith('.tar.gz')]
    print(f"Found {len(tar_gz_files)} tar.gz files to test")

    successful = 0
    failed = 0

    for i, filename in enumerate(tar_gz_files, 1):
        print(f"\n[{i}/{len(tar_gz_files)}] Testing: {filename}")
        file_path = os.path.join(tar_gz_dir, filename)

        try:
            parser = EFileParser()
            result = parser.parse_file(file_path)

            if 'error' in result:
                print(f"❌ FAILED: {result['error']}")
                results[filename] = {
                    'status': 'failed',
                    'error': result['error'],
                    'file_path': file_path
                }
                failed += 1
            else:
                records_count = len(result.get('data_records', []))
                files_parsed = result.get('archive_stats', {}).get('total_files', 0)
                print(f"✅ SUCCESS: {records_count} records from {files_parsed} files")
                results[filename] = {
                    'status': 'success',
                    'records': records_count,
                    'files_parsed': files_parsed,
                    'file_path': file_path
                }
                successful += 1

        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            results[filename] = {
                'status': 'exception',
                'error': str(e),
                'file_path': file_path
            }
            failed += 1

    print(f"\nTAR.GZ SUMMARY: {successful} success, {failed} failed")
    return results

def test_102e2601_files():
    """Test each dat file in 102E2601 individually"""
    print("\n" + "="*80)
    print("TESTING DAT FILES IN 102E2601/")
    print("="*80)

    results = {}
    dat_dir = os.path.join(os.getcwd(), '102E2601')

    if not os.path.exists(dat_dir):
        print(f"Directory not found: {dat_dir}")
        return results

    dat_files = [f for f in os.listdir(dat_dir) if f.endswith('.dat')]
    print(f"Found {len(dat_files)} dat files to test")

    successful = 0
    failed = 0

    for i, filename in enumerate(dat_files, 1):
        if i % 100 == 0:  # Progress indicator
            print(f"Processed {i}/{len(dat_files)} files...")

        file_path = os.path.join(dat_dir, filename)

        try:
            parser = EFileParser()
            result = parser.parse_file(file_path)

            if 'error' in result:
                results[filename] = {
                    'status': 'failed',
                    'error': result['error'],
                    'file_path': file_path
                }
                failed += 1
            else:
                records_count = len(result.get('data_records', []))
                results[filename] = {
                    'status': 'success',
                    'records': records_count,
                    'file_path': file_path
                }
                successful += 1

        except Exception as e:
            results[filename] = {
                'status': 'exception',
                'error': str(e),
                'file_path': file_path
            }
            failed += 1

    print(f"\n102E2601 SUMMARY: {successful} success, {failed} failed")
    return results

def test_20260114_files():
    """Test each dat file in 20260114 subdirectories individually"""
    print("\n" + "="*80)
    print("TESTING DAT FILES IN 20260114/ SUBDIRECTORIES")
    print("="*80)

    results = {}
    main_dir = os.path.join(os.getcwd(), '20260114')

    if not os.path.exists(main_dir):
        print(f"Directory not found: {main_dir}")
        return results

    subdirs = [d for d in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, d))]
    print(f"Found {len(subdirs)} subdirectories")

    total_successful = 0
    total_failed = 0

    for subdir in subdirs:
        print(f"\nProcessing subdirectory: {subdir}")
        subdir_path = os.path.join(main_dir, subdir)
        dat_files = [f for f in os.listdir(subdir_path) if f.endswith('.dat')]
        print(f"  Found {len(dat_files)} dat files")

        successful = 0
        failed = 0

        for filename in dat_files:
            file_path = os.path.join(subdir_path, filename)

            try:
                parser = EFileParser()
                result = parser.parse_file(file_path)

                if 'error' in result:
                    results[f"{subdir}/{filename}"] = {
                        'status': 'failed',
                        'error': result['error'],
                        'file_path': file_path
                    }
                    failed += 1
                else:
                    records_count = len(result.get('data_records', []))
                    results[f"{subdir}/{filename}"] = {
                        'status': 'success',
                        'records': records_count,
                        'file_path': file_path
                    }
                    successful += 1

            except Exception as e:
                results[f"{subdir}/{filename}"] = {
                    'status': 'exception',
                    'error': str(e),
                    'file_path': file_path
                }
                failed += 1

        print(f"  {subdir} SUMMARY: {successful} success, {failed} failed")
        total_successful += successful
        total_failed += failed

    print(f"\n20260114 TOTAL SUMMARY: {total_successful} success, {total_failed} failed")
    return results

def main():
    """Run comprehensive individual file tests"""
    print("STARTING COMPREHENSIVE INDIVIDUAL FILE TESTING")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_results = {
        'tar_gz_files': {},
        'dat_files_102e2601': {},
        'dat_files_20260114': {},
        'summary': {},
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Test tar.gz files
    all_results['tar_gz_files'] = test_tar_gz_files()

    # Test 102E2601 files
    all_results['dat_files_102e2601'] = test_102e2601_files()

    # Test 20260114 files
    all_results['dat_files_20260114'] = test_20260114_files()

    # Calculate overall summary
    tar_gz_success = sum(1 for r in all_results['tar_gz_files'].values() if r['status'] == 'success')
    dat_102e2601_success = sum(1 for r in all_results['dat_files_102e2601'].values() if r['status'] == 'success')
    dat_20260114_success = sum(1 for r in all_results['dat_files_20260114'].values() if r['status'] == 'success')

    tar_gz_total = len(all_results['tar_gz_files'])
    dat_102e2601_total = len(all_results['dat_files_102e2601'])
    dat_20260114_total = len(all_results['dat_files_20260114'])

    total_successful = tar_gz_success + dat_102e2601_success + dat_20260114_success
    total_files = tar_gz_total + dat_102e2601_total + dat_20260114_total

    all_results['summary'] = {
        'tar_gz_files': {'success': tar_gz_success, 'total': tar_gz_total, 'rate': f"{tar_gz_success/tar_gz_total*100:.2f}%" if tar_gz_total > 0 else "N/A"},
        'dat_files_102e2601': {'success': dat_102e2601_success, 'total': dat_102e2601_total, 'rate': f"{dat_102e2601_success/dat_102e2601_total*100:.2f}%" if dat_102e2601_total > 0 else "N/A"},
        'dat_files_20260114': {'success': dat_20260114_success, 'total': dat_20260114_total, 'rate': f"{dat_20260114_success/dat_20260114_total*100:.2f}%" if dat_20260114_total > 0 else "N/A"},
        'overall': {'success': total_successful, 'total': total_files, 'rate': f"{total_successful/total_files*100:.2f}%" if total_files > 0 else "N/A"}
    }

    print("\n" + "="*80)
    print("FINAL COMPREHENSIVE TEST RESULTS")
    print("="*80)
    print(f"tar.gz files (102E文本数据2026.01): {tar_gz_success}/{tar_gz_total} ({all_results['summary']['tar_gz_files']['rate']})")
    print(f"dat files (102E2601): {dat_102e2601_success}/{dat_102e2601_total} ({all_results['summary']['dat_files_102e2601']['rate']})")
    print(f"dat files (20260114): {dat_20260114_success}/{dat_20260114_total} ({all_results['summary']['dat_files_20260114']['rate']})")
    print(f"TOTAL: {total_successful}/{total_files} ({all_results['summary']['overall']['rate']})")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Save detailed results
    with open('comprehensive_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print("Detailed results saved to comprehensive_test_results.json")

if __name__ == '__main__':
    main()
