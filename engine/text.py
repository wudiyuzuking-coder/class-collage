from pathlib import Path
from typing import Any, Optional
import random

from PIL import Image, ImageDraw, ImageFont

from engine.template import DEFAULT_TEMPLATE

ROOT_DIR = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT_DIR / "assets" / "fonts"
FONT_EXTENSIONS = {".ttf", ".otf", ".ttc"}

# 常见中文字体路径。优先找真实文件路径，避免中文被画成方块或乱码。
SYSTEM_FONT_PATHS = (
    # Windows
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/msyhbd.ttc"),
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/simsun.ttc"),
    # macOS
    Path("/System/Library/Fonts/PingFang.ttc"),
    Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
    Path("/System/Library/Fonts/STHeiti Light.ttc"),
    Path("/Library/Fonts/Arial Unicode.ttf"),
    # Linux
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
)

def _choice_from_template(template: dict[str, Any], key: str) -> str:
    """从模板列表中随机取一个值；坏配置会回退默认模板。"""
    values = template.get(key)
    if not isinstance(values, list) or not values:
        values = DEFAULT_TEMPLATE[key]
    return random.choice(values)


def random_background_color(template: dict[str, Any]) -> str:
    """从模板中随机返回背景色。"""
    return _choice_from_template(template, "background_colors")


def random_title_color(template: dict[str, Any]) -> str:
    """从模板中随机返回标题颜色。"""
    return _choice_from_template(template, "title_colors")


def random_subtitle_color(template: dict[str, Any]) -> str:
    """从模板中随机返回底部文案颜色。"""
    return _choice_from_template(template, "subtitle_colors")


def random_title(template: dict[str, Any]) -> str:
    """从模板中随机返回顶部标题。"""
    return _choice_from_template(template, "titles")


def random_footer(template: dict[str, Any]) -> str:
    """从模板中随机返回底部文案。"""
    return _choice_from_template(template, "subtitles")


def random_english_slogan(template: dict[str, Any]) -> str:
    """从模板中随机返回英文祝福语。"""
    return _choice_from_template(template, "english_slogans")


def _asset_fonts() -> list[Path]:
    """读取 assets/fonts/ 中的字体文件，主要用于英文装饰文案。"""
    if not FONT_DIR.exists():
        return []

    return [
        font_path
        for font_path in sorted(FONT_DIR.iterdir())
        if font_path.is_file() and font_path.suffix.lower() in FONT_EXTENSIONS
    ]


def _contains_cjk(text: str) -> bool:
    """判断文本中是否包含中文字符；中文不使用只支持英文的装饰字体。"""
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def _path_has_cjk(path: Path) -> bool:
    """中文文件名的字体用于中文，英文文件名的字体用于英文。"""
    return _contains_cjk(path.stem)


def _candidate_fonts(
    text: str = "",
    prefer_english: bool = False,
    randomize: bool = False,
) -> list[Path]:
    """按文字类型返回字体候选列表，避免英文装饰字体把中文画成方块。"""
    has_cjk = _contains_cjk(text)
    fonts: list[Path] = []
    asset_fonts = _asset_fonts()

    if has_cjk:
        fonts.extend(font_path for font_path in asset_fonts if _path_has_cjk(font_path))
    elif prefer_english:
        fonts.extend(font_path for font_path in asset_fonts if not _path_has_cjk(font_path))

    fonts.extend(font_path for font_path in SYSTEM_FONT_PATHS if font_path.exists())

    if randomize and len(fonts) > 1:
        random.shuffle(fonts)
    return fonts


def load_font(
    size: int = 48,
    text: str = "",
    prefer_english: bool = False,
    randomize: bool = False,
) -> ImageFont.ImageFont:
    """加载字体；找不到字体时回退到 Pillow 默认字体，保证程序不报错。"""
    for font_path in _candidate_fonts(text, prefer_english, randomize):
        try:
            return ImageFont.truetype(str(font_path), size)
        except OSError:
            continue

    return ImageFont.load_default()


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    """计算文字宽高。"""
    text_box = draw.textbbox((0, 0), text, font=font)
    return text_box[2] - text_box[0], text_box[3] - text_box[1]


def _fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    font_size: int,
    min_size: int = 24,
    prefer_english: bool = False,
    randomize_font: bool = False,
) -> ImageFont.ImageFont:
    """根据文字区域自动缩小字号，避免自定义长标题溢出。"""
    current_size = font_size
    while current_size >= min_size:
        font = load_font(
            current_size,
            text=text,
            prefer_english=prefer_english,
            randomize=randomize_font,
        )
        text_width, text_height = _text_size(draw, text, font)
        if text_width <= max_width and text_height <= max_height:
            return font
        current_size -= 2

    return load_font(
        min_size,
        text=text,
        prefer_english=prefer_english,
        randomize=randomize_font,
    )


def draw_centered_text(
    image: Image.Image,
    text: str,
    box: tuple[int, int, int, int],
    fill: str = "#243042",
    font_size: int = 48,
    prefer_english: bool = False,
    randomize_font: bool = False,
) -> None:
    """在指定区域内居中绘制文字。"""
    draw = ImageDraw.Draw(image)
    left, top, right, bottom = box
    max_width = max(1, right - left - 80)
    max_height = max(1, bottom - top - 12)
    font = _fit_font(
        draw,
        text,
        max_width,
        max_height,
        font_size,
        prefer_english=prefer_english,
        randomize_font=randomize_font,
    )
    text_width, text_height = _text_size(draw, text, font)

    x = left + (right - left - text_width) / 2
    y = top + (bottom - top - text_height) / 2
    draw.text((x, y), text, fill=fill, font=font)


def default_font(size: int = 28) -> ImageFont.ImageFont:
    """保留旧函数名，方便项目里其他模块继续调用。"""
    return load_font(size)
