#!/usr/bin/env python3
"""
Batch test script for E-File parser
Tests all tar.gz files in 102E文本数据2026.01/, dat files in 102E2601/, and dat files in 20260114/ subdirectories
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
        logging.FileHandler('batch_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Run batch tests"""
    print("Starting batch tests...")

    test_results = {
        'tar_gz_files': {},
        'dat_files_102e2601': {},
        'dat_files_20260114': {}
    }

    total_tests = 0
    successful_tests = 0

    # Test tar.gz files in 102E文本数据2026.01/
    tar_gz_dir = os.path.join(os.getcwd(), '102E文本数据2026.01')
    if os.path.exists(tar_gz_dir):
        print("Testing tar.gz files...")
        tar_gz_files = [f for f in os.listdir(tar_gz_dir) if f.endswith('.tar.gz')]
        total_tests += len(tar_gz_files)
        print(f"Found {len(tar_gz_files)} tar.gz files")

        for i, filename in enumerate(tar_gz_files):
            if (i + 1) % 5 == 0:  # Progress every 5 files
                print(f"Processed {i+1}/{len(tar_gz_files)} tar.gz files...")

            file_path = os.path.join(tar_gz_dir, filename)

            try:
                parser = EFileParser()
                result = parser.parse_file(file_path)

                if 'error' in result:
                    test_results['tar_gz_files'][filename] = {
                        'status': 'failed',
                        'error': result['error']
                    }
                    print(f"❌ Failed: {filename} - {result['error']}")
                else:
                    test_results['tar_gz_files'][filename] = {
                        'status': 'success',
                        'records': len(result.get('data_records', [])),
                        'files_parsed': result.get('archive_stats', {}).get('total_files', 0)
                    }
                    successful_tests += 1
                    print(f"✅ Success: {filename} - {len(result.get('data_records', []))} records")

            except Exception as e:
                test_results['tar_gz_files'][filename] = {
                    'status': 'failed',
                    'error': str(e)
                }
                print(f"❌ Exception: {filename} - {str(e)}")

    # Test dat files in 102E2601/
    dat_dir = os.path.join(os.getcwd(), '102E2601')
    if os.path.exists(dat_dir):
        print("\nTesting 102E2601 dat files...")
        dat_files = [f for f in os.listdir(dat_dir) if f.endswith('.dat')]
        total_tests += len(dat_files)
        print(f"Found {len(dat_files)} dat files")

        for i, filename in enumerate(dat_files):
            if (i + 1) % 20 == 0:  # Progress every 20 files
                print(f"Processed {i+1}/{len(dat_files)} dat files...")

            file_path = os.path.join(dat_dir, filename)

            try:
                parser = EFileParser()
                result = parser.parse_file(file_path)

                if 'error' in result:
                    test_results['dat_files_102e2601'][filename] = {
                        'status': 'failed',
                        'error': result['error']
                    }
                    print(f"❌ Failed: {filename} - {result['error']}")
                else:
                    test_results['dat_files_102e2601'][filename] = {
                        'status': 'success',
                        'records': len(result.get('data_records', []))
                    }
                    successful_tests += 1
                    print(f"✅ Success: {filename} - {len(result.get('data_records', []))} records")

            except Exception as e:
                test_results['dat_files_102e2601'][filename] = {
                    'status': 'failed',
                    'error': str(e)
                }
                print(f"❌ Exception: {filename} - {str(e)}")

    # Test dat files in 20260114/ subdirectories
    main_dir = os.path.join(os.getcwd(), '20260114')
    if os.path.exists(main_dir):
        print("\nTesting 20260114 dat files...")
        subdirs = [d for d in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, d))]
        print(f"Found {len(subdirs)} subdirectories")

        for subdir in subdirs:
            print(f"Processing subdirectory: {subdir}")
            subdir_path = os.path.join(main_dir, subdir)
            dat_files = [f for f in os.listdir(subdir_path) if f.endswith('.dat')]
            total_tests += len(dat_files)
            print(f"  Found {len(dat_files)} dat files in {subdir}")

            for filename in dat_files:
                file_path = os.path.join(subdir_path, filename)

                try:
                    parser = EFileParser()
                    result = parser.parse_file(file_path)

                    if 'error' in result:
                        test_results['dat_files_20260114'][f"{subdir}/{filename}"] = {
                            'status': 'failed',
                            'error': result['error']
                        }
                        print(f"❌ Failed: {subdir}/{filename} - {result['error']}")
                    else:
                        test_results['dat_files_20260114'][f"{subdir}/{filename}"] = {
                            'status': 'success',
                            'records': len(result.get('data_records', []))
                        }
                        successful_tests += 1
                        print(f"✅ Success: {subdir}/{filename} - {len(result.get('data_records', []))} records")

                except Exception as e:
                    test_results['dat_files_20260114'][f"{subdir}/{filename}"] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    print(f"❌ Exception: {subdir}/{filename} - {str(e)}")

    # Calculate and display summary
    tar_gz_success = sum(1 for r in test_results['tar_gz_files'].values() if r['status'] == 'success')
    dat_102e2601_success = sum(1 for r in test_results['dat_files_102e2601'].values() if r['status'] == 'success')
    dat_20260114_success = sum(1 for r in test_results['dat_files_20260114'].values() if r['status'] == 'success')

    print("\n" + "="*60)
    print("BATCH TEST RESULTS SUMMARY")
    print("="*60)
    print(f"tar.gz files (102E文本数据2026.01): {tar_gz_success}/{len(test_results['tar_gz_files'])} successful")
    print(f"dat files (102E2601): {dat_102e2601_success}/{len(test_results['dat_files_102e2601'])} successful")
    print(f"dat files (20260114): {dat_20260114_success}/{len(test_results['dat_files_20260114'])} successful")
    print(f"Total: {successful_tests}/{total_tests} successful ({successful_tests/total_tests*100:.1f}%)")
    print("="*60)

    # Save detailed results
    with open('batch_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)

    print(f"Detailed results saved to batch_test_results.json")

if __name__ == '__main__':
    main()
