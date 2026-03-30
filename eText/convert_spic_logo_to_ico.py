#!/usr/bin/env python3
"""
Convert SPIC logo PNG to ICO format
"""
import os
from PIL import Image

def convert_png_to_ico():
    """Convert PNG to ICO format with multiple sizes"""
    # Source file path
    source_png = r"D:\001\eTextDTA\logo\spic_logo.png"
    
    # Output file path
    output_ico = r"D:\001\eTextDTA\logo\spic_logo.ico"
    
    # Check if source file exists
    if not os.path.exists(source_png):
        print(f"Error: Source file not found: {source_png}")
        return False
    
    try:
        # Open the PNG image
        with Image.open(source_png) as img:
            print(f"Source image: {source_png}")
            print(f"Original size: {img.size}")
            print(f"Original format: {img.format}")
            print(f"Original mode: {img.mode}")
            
            # ICO format supports multiple sizes
            # Common sizes for Windows icons: 16x16, 32x32, 48x48, 256x256
            sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
            
            # Create list of resized images
            icon_images = []
            for size in sizes:
                resized_img = img.resize(size, Image.Resampling.LANCZOS)
                icon_images.append(resized_img)
            
            # Save as ICO
            icon_images[0].save(
                output_ico,
                format='ICO',
                sizes=[(img.size[0], img.size[1]) for img in icon_images]
            )
            
            print(f"Successfully converted to: {output_ico}")
            print(f"Created ICO with sizes: {[img.size for img in icon_images]}")
            
            # Verify the file was created
            if os.path.exists(output_ico):
                file_size = os.path.getsize(output_ico)
                print(f"Output file size: {file_size} bytes")
                return True
            else:
                print("Error: ICO file was not created")
                return False
                
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

if __name__ == "__main__":
    success = convert_png_to_ico()
    if success:
        print("\nConversion completed successfully!")
    else:
        print("\nConversion failed!")