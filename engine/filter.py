from typing import Optional

from PIL import Image, ImageEnhance, ImageFilter, ImageStat


SUPPORTED_FILTERS = {"none", "soft", "vivid", "warm", "cool"}
DEFAULT_FILTER = "soft"


def adjust_brightness(image: Image.Image, factor: float) -> Image.Image:
    """调整亮度，factor 大于 1 会变亮，小于 1 会变暗。"""
    return ImageEnhance.Brightness(image).enhance(factor)


def adjust_contrast(image: Image.Image, factor: float) -> Image.Image:
    """调整对比度，factor 大于 1 会增强对比。"""
    return ImageEnhance.Contrast(image).enhance(factor)


def adjust_color(image: Image.Image, factor: float) -> Image.Image:
    """调整饱和度，factor 大于 1 会让颜色更鲜明。"""
    return ImageEnhance.Color(image).enhance(factor)


def adjust_sharpness(image: Image.Image, factor: float) -> Image.Image:
    """调整锐度，factor 大于 1 会让细节更清晰。"""
    return ImageEnhance.Sharpness(image).enhance(factor)


def analyze_image(image: Image.Image) -> dict:
    """分析图片基础信息：平均亮度、粗略对比度、粗略饱和度。"""
    image = image.convert("RGB")
    gray = image.convert("L")

    gray_stat = ImageStat.Stat(gray)
    rgb_stat = ImageStat.Stat(image)

    # 平均亮度：灰度平均值，范围约 0~255。
    brightness = gray_stat.mean[0]

    # 粗略对比度：灰度标准差，越大说明明暗层次越强。
    contrast = gray_stat.stddev[0]

    # 粗略饱和度：用 RGB 通道差异估计，差异越大说明颜色越鲜明。
    channel_means = rgb_stat.mean
    saturation = max(channel_means) - min(channel_means)

    return {
        "brightness": brightness,
        "contrast": contrast,
        "saturation": saturation,
    }


def auto_enhance_image(image: Image.Image) -> Image.Image:
    """根据图片状态做轻量自动优化，保持自然不过度。"""
    image = image.convert("RGB")
    info = analyze_image(image)

    brightness = info["brightness"]
    contrast = info["contrast"]
    saturation = info["saturation"]

    # 偏暗时轻微提亮，已经很亮时不再继续抬亮度。
    if brightness < 95:
        image = adjust_brightness(image, 1.12)
    elif brightness < 125:
        image = adjust_brightness(image, 1.07)
    elif brightness > 215:
        image = adjust_brightness(image, 0.98)

    # 对比度偏低时轻微增强，避免照片发灰。
    if contrast < 38:
        image = adjust_contrast(image, 1.09)
    elif contrast < 52:
        image = adjust_contrast(image, 1.04)

    # 色彩偏灰时轻微增加饱和度，颜色足够时少动或不动。
    if saturation < 18:
        image = adjust_color(image, 1.10)
    elif saturation < 35:
        image = adjust_color(image, 1.05)
    elif saturation > 95:
        image = adjust_color(image, 0.98)

    # 非常轻的锐化，让照片卡片更清晰。
    image = adjust_sharpness(image, 1.04)
    return image


def apply_warm_tone(image: Image.Image, strength: float = 0.08) -> Image.Image:
    """应用轻微暖色调，适度增强红色和绿色通道。"""
    image = image.convert("RGB")
    red, green, blue = image.split()
    red = red.point(lambda value: min(255, int(value * (1 + strength))))
    green = green.point(lambda value: min(255, int(value * (1 + strength * 0.45))))
    blue = blue.point(lambda value: max(0, int(value * (1 - strength * 0.25))))
    return Image.merge("RGB", (red, green, blue))


def apply_cool_tone(image: Image.Image, strength: float = 0.08) -> Image.Image:
    """应用轻微冷色调，适度增强蓝色通道。"""
    image = image.convert("RGB")
    red, green, blue = image.split()
    red = red.point(lambda value: max(0, int(value * (1 - strength * 0.2))))
    green = green.point(lambda value: min(255, int(value * (1 + strength * 0.15))))
    blue = blue.point(lambda value: min(255, int(value * (1 + strength))))
    return Image.merge("RGB", (red, green, blue))


def normalize_filter_name(filter_name: Optional[str]) -> str:
    """校验滤镜名称；未知滤镜回退到默认滤镜。"""
    safe_name = (filter_name or DEFAULT_FILTER).lower()
    if safe_name not in SUPPORTED_FILTERS:
        return DEFAULT_FILTER
    return safe_name


def apply_filter(image: Image.Image, filter_name: str) -> Image.Image:
    """根据预设名称应用轻量滤镜。"""
    filter_name = normalize_filter_name(filter_name)
    image = image.convert("RGB")

    if filter_name == "none":
        return image

    if filter_name == "soft":
        image = adjust_brightness(image, 1.04)
        image = adjust_contrast(image, 1.04)
        image = adjust_color(image, 1.06)
        image = image.filter(ImageFilter.SMOOTH)
        return image

    if filter_name == "vivid":
        image = adjust_contrast(image, 1.10)
        image = adjust_color(image, 1.16)
        image = adjust_sharpness(image, 1.08)
        return image

    if filter_name == "warm":
        image = adjust_brightness(image, 1.04)
        image = adjust_color(image, 1.08)
        return apply_warm_tone(image)

    if filter_name == "cool":
        image = adjust_brightness(image, 1.03)
        image = adjust_contrast(image, 1.05)
        return apply_cool_tone(image)

    return image
