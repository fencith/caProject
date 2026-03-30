#!/usr/bin/env python3
"""
Create a better Windows icon with multiple sizes and proper formatting
"""
import os
from PIL import Image

def create_better_icon(input_path, output_path):
    """Create a high-quality Windows icon with multiple sizes"""
    try:
        # Open the PNG image
        img = Image.open(input_path)

        # Convert to RGBA to ensure proper transparency handling
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Define Windows icon sizes (in order of preference)
        sizes = [
            (256, 256),
            (128, 128),
            (96, 96),
            (64, 64),
            (48, 48),
            (32, 32),
            (24, 24),
            (16, 16)
        ]

        # Create the ICO file with all sizes
        img.save(output_path, format='ICO', sizes=sizes)

        print(f"✅ Successfully created high-quality icon: {output_path}")
        print(f"📏 Icon sizes: {[f'{s[0]}x{s[1]}' for s in sizes]}")
        print(f"💾 File size: {os.path.getsize(output_path)} bytes")

        return True
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        return False

if __name__ == "__main__":
    input_file = "spic-logo.png"
    output_file = "spic-logo-final.ico"

    if not os.path.exists(input_file):
        print(f"❌ Input file {input_file} not found")
        exit(1)

    success = create_better_icon(input_file, output_file)

    if success:
        print(f"🎉 High-quality icon created: {output_file}")
    else:
        print("❌ Icon creation failed")
        exit(1)