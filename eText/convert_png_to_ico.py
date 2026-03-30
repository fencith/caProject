#!/usr/bin/env python3
"""
Convert PNG to ICO for Windows application icon
"""
import os
from PIL import Image

def convert_png_to_ico(input_path, output_path):
    """Convert PNG file to ICO format"""
    try:
        # Open the PNG image
        img = Image.open(input_path)

        # Convert to ICO format (Windows icon format)
        img.save(output_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])

        print(f"✅ Successfully converted {input_path} to {output_path}")
        print(f"📏 Icon sizes: 256x256, 128x128, 64x64, 48x48, 32x32, 16x16")
        print(f"💾 File size: {os.path.getsize(output_path)} bytes")

        return True
    except Exception as e:
        print(f"❌ Error converting PNG to ICO: {e}")
        return False

if __name__ == "__main__":
    input_file = "spic-logo.png"
    output_file = "spic-logo-new.ico"

    if not os.path.exists(input_file):
        print(f"❌ Input file {input_file} not found")
        exit(1)

    success = convert_png_to_ico(input_file, output_file)

    if success:
        print(f"🎉 Conversion complete! New icon: {output_file}")
    else:
        print("❌ Conversion failed")
        exit(1)