from efile_parser import parse_efile, generate_html_report
import os

def demo_parse():
    print("=" * 60)
    print("E文件解析工具演示")
    print("=" * 60)
    print()

    examples = [
        ("风机单机信息", "20260114/FJDZ/FD_GD.GDZJYHHB_FDJZ_20260114_000000.dat"),
        ("升压站信息", "20260114/SYZXX/FD_GD.GDZJYHHB_SYZXX_20260114_000000.dat"),
        ("总体气象信息", "20260114/ZTXX-QXHJ/FD_GD.GDZJYHHB_ZTXX-QXHJ_20260114_000000.dat"),
    ]

    for name, filepath in examples:
        if os.path.exists(filepath):
            print(f"正在解析: {name}")
            print(f"文件: {filepath}")

            try:
                result = parse_efile(filepath)
                html = generate_html_report(result)

                output_file = filepath.replace('.dat', '_report.html')
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html)

                print("  [OK] Parse succeeded")
                print(f"  - Sections: {len(result['sections'])}")
                print(f"  - Tables: {sum(len(s['tables']) for s in result['sections'])}")
                print(f"  - Total rows: {sum(sum(t['row_count'] for t in s['tables']) for s in result['sections'])}")
                print(f"  - Report: {output_file}")
                print()
            except Exception as e:
                print(f"  [FAIL] Parse failed: {e}")
                print()
        else:
            print(f"文件不存在: {filepath}")
            print()

    print("=" * 60)
    print("演示完成！")
    print("=" * 60)
    print()
    print("提示：")
    print("1. 使用 'python app.py' 启动Web应用")
    print("2. 访问 http://localhost:5000 上传文件")
    print("3. 或直接在浏览器中打开生成的HTML报告")

if __name__ == "__main__":
    demo_parse()
