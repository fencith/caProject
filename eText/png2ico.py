from PIL import Image
import os

def png_to_ico(png_path, ico_path, sizes=None):
    """
    将 PNG 转换为 ICO
    :param png_path: 输入 PNG 文件路径
    :param ico_path: 输出 ICO 文件路径
    :param sizes: ICO 包含的尺寸列表，默认 [16,32,48,64,256]
    """
    if sizes is None:
        sizes = [(16,16), (32,32), (48,48), (64,64), (256,256)]
    
    # 打开 PNG 图片（必须是 RGBA 模式，否则透明通道会丢失）
    try:
        img = Image.open(png_path).convert("RGBA")
        # 调整图片大小并保存为 ICO
        img.save(ico_path, format='ICO', sizes=sizes)
        print(f"✅ 转换成功：{ico_path}")
    except Exception as e:
        print(f"❌ 转换失败：{e}")

# ==================== 用法示例 ====================
if __name__ == "__main__":
    # 单文件转换
    png_to_ico(
        png_path=r"D:\001\eText\spic_logo.png",   # 替换为你的 PNG 路径
        ico_path=r"D:\001\eText\spic_icon.ico"  # 输出 ICO 路径
    )

    # 批量转换（转换指定文件夹下所有 PNG）
    # input_dir = "png_icons"
    # output_dir = "ico_icons"
    # os.makedirs(output_dir, exist_ok=True)
    # for file in os.listdir(input_dir):
    #     if file.endswith(".png"):
    #         png_path = os.path.join(input_dir, file)
    #         ico_path = os.path.join(output_dir, file.replace(".png", ".ico"))
    #         png_to_ico(png_path, ico_path)
    