from PIL import Image, ImageDraw, ImageFilter


def add_rounded_corners(image: Image.Image, radius: int = 28) -> Image.Image:
    """给图片添加圆角透明蒙版。"""
    rounded = image.convert("RGBA")
    mask = Image.new("L", rounded.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, rounded.width, rounded.height), radius=radius, fill=255)
    rounded.putalpha(mask)
    return rounded


def add_border(
    image: Image.Image,
    border_width: int = 12,
    border_color: str = "#ffffff",
    radius: int = 28,
) -> Image.Image:
    """给圆角图片添加白色边框。"""
    bordered_size = (
        image.width + border_width * 2,
        image.height + border_width * 2,
    )
    bordered = Image.new("RGBA", bordered_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(bordered)

    # 先画外层白色圆角矩形，再把图片贴到中间
    draw.rounded_rectangle(
        (0, 0, bordered.width - 1, bordered.height - 1),
        radius=radius + border_width,
        fill=border_color,
    )
    bordered.alpha_composite(image, (border_width, border_width))
    return bordered


def add_shadow(
    image: Image.Image,
    radius: int = 40,
    blur: int = 18,
    offset: tuple[int, int] = (0, 8),
    shadow_color: tuple[int, int, int, int] = (58, 46, 33, 52),
) -> Image.Image:
    """给卡片添加轻微阴影，返回包含阴影的透明图片。"""
    extra = blur + max(abs(offset[0]), abs(offset[1]))
    shadow_size = (image.width + extra * 2, image.height + extra * 2)
    shadow = Image.new("RGBA", shadow_size, (255, 255, 255, 0))

    shadow_box = (
        extra + offset[0],
        extra + offset[1],
        extra + offset[0] + image.width,
        extra + offset[1] + image.height,
    )
    shadow_layer = Image.new("RGBA", shadow_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(shadow_layer)
    draw.rounded_rectangle(shadow_box, radius=radius, fill=shadow_color)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(blur))

    shadow.alpha_composite(shadow_layer)
    shadow.alpha_composite(image, (extra, extra))
    return shadow


def create_photo_card(
    image: Image.Image,
    size: tuple[int, int],
    radius: int = 28,
    border_width: int = 12,
) -> Image.Image:
    """创建带圆角、白边和阴影的照片卡片，整体尺寸不超过指定区域。"""
    width, height = size

    # 阴影留在卡片内部，避免贴到画布时溢出边界
    shadow_blur = 18
    shadow_offset_y = 8
    shadow_padding = shadow_blur + shadow_offset_y
    card_width = max(1, width - shadow_padding * 2)
    card_height = max(1, height - shadow_padding * 2)
    photo_width = max(1, card_width - border_width * 2)
    photo_height = max(1, card_height - border_width * 2)

    photo = image.resize((photo_width, photo_height), Image.Resampling.LANCZOS)
    rounded_photo = add_rounded_corners(photo, radius=radius)
    bordered_photo = add_border(
        rounded_photo,
        border_width=border_width,
        border_color="#ffffff",
        radius=radius,
    )
    shadowed_photo = add_shadow(
        bordered_photo,
        radius=radius + border_width,
        blur=shadow_blur,
        offset=(0, shadow_offset_y),
    )

    card = Image.new("RGBA", size, (255, 255, 255, 0))
    x = (width - shadowed_photo.width) // 2
    y = (height - shadowed_photo.height) // 2
    card.alpha_composite(shadowed_photo, (x, y))
    return card


def draw_frame(image: Image.Image, color: str = "#1f2937", width: int = 8) -> Image.Image:
    """保留旧函数，方便旧代码继续调用。"""
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width - 1, image.height - 1), outline=color, width=width)
    return image
