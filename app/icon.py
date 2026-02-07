from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_tray_image(text="UW", size=128):

    BASE_DIR = Path(__file__).resolve().parent.parent

    """
    text: 图标显示文字
    size: 图标尺寸（建议 >= 128）
    返回 PIL.Image 对象
    """
    # 创建透明背景
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 半透明白色圆形背景
    bg_color = (255, 255, 255, 180)  # 白色半透明
    draw.ellipse([(0, 0), (size, size)], fill=bg_color)

    # 字体
    font_path = BASE_DIR / "font/GalmuriMono9.ttf";
    font_size = int(size * 0.5)  # 文字占图标高度 50%
    font = ImageFont.truetype(str(font_path), font_size)

    # 文字边界测量
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # 居中绘制
    text_x = (size - text_w) // 2
    text_y = (size - text_h) // 2
    draw.text((text_x, text_y), text, font=font, fill=(0, 0, 0, 255))  # 黑色文字

    return img
