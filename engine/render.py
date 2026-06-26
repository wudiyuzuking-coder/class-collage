import random
from pathlib import Path
from typing import Optional

from PIL import Image, ImageOps

from engine.assets import load_random_background_image, load_random_frame_image
from engine.decorate import create_photo_card
from engine.filter import DEFAULT_FILTER, apply_filter, auto_enhance_image
from engine.frame import apply_photo_frame, choose_photo_frame
from engine.layout import ImageBox, get_image_layout
from engine.sticker import add_random_stickers
from engine.template import load_template
from engine.text import (
    draw_centered_text,
    random_background_color,
    random_english_slogan,
    random_footer,
    random_subtitle_color,
    random_title,
    random_title_color,
)


# 适合发给家长的竖版图片尺寸。
CANVAS_SIZE = (1080, 1350)

# 顶部标题区和底部文案区的高度。
TITLE_AREA_HEIGHT = 120
FOOTER_AREA_HEIGHT = 120

# 中间图片区范围。
IMAGE_AREA_TOP = 150
IMAGE_AREA_BOTTOM = 1180


def _create_canvas(template: dict) -> Image.Image:
    """创建画布：优先使用模板背景图，失败时回退纯色背景。"""
    background = load_random_background_image(template, CANVAS_SIZE)
    if background is None:
        return Image.new("RGB", CANVAS_SIZE, random_background_color(template))

    # 背景图可能带透明通道，先铺在纯色底上再合成。
    canvas = Image.new("RGBA", CANVAS_SIZE, random_background_color(template))
    canvas.alpha_composite(background)
    return canvas.convert("RGB")


def _paste_cropped_image(
    canvas: Image.Image,
    image_path: Path,
    box: ImageBox,
    filter_name: str,
    auto_enhance: bool,
    photo_frame_path: Optional[Path],
) -> None:
    """读取图片、自动优化、应用滤镜、居中裁剪，并贴到指定区域。"""
    with Image.open(image_path) as source:
        source = ImageOps.exif_transpose(source).convert("RGB")
        if auto_enhance:
            source = auto_enhance_image(source)
        source = apply_filter(source, filter_name)
        cropped = ImageOps.fit(
            source,
            (box.width, box.height),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
        photo_card = create_photo_card(cropped, (box.width, box.height))
        if photo_frame_path is not None:
            photo_card = apply_photo_frame(photo_card, photo_frame_path)
        canvas.paste(photo_card, (box.x, box.y), photo_card)


def _resolve_photo_frame_dir(
    template: dict,
    theme: str,
    photo_frame_theme: Optional[str],
    no_photo_frame: bool,
) -> Optional[str]:
    """根据命令行和模板配置决定照片相框来源。"""
    if no_photo_frame:
        return None

    requested = (photo_frame_theme or "random").lower()
    if requested == "none":
        return None
    if requested != "random":
        return requested
    if not template.get("use_photo_frame", False):
        return None

    frame_dir = template.get("photo_frame_dir") or theme or "cute"
    return frame_dir if isinstance(frame_dir, str) else "cute"


def _apply_frame(canvas: Image.Image, template: dict) -> Image.Image:
    """最后叠加模板边框图；没有边框图时直接返回原图。"""
    frame = load_random_frame_image(template, CANVAS_SIZE)
    if frame is None:
        return canvas

    canvas = canvas.convert("RGBA")
    canvas.alpha_composite(frame)
    return canvas.convert("RGB")


def render_class_record(
    image_paths: list[Path],
    output_path: Path,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    theme: str = "cute",
    filter_name: str = DEFAULT_FILTER,
    auto_enhance: bool = True,
    sticker_theme: Optional[str] = "random",
    photo_frame_theme: Optional[str] = "random",
    no_photo_frame: bool = False,
) -> Path:
    """生成课堂记录拼图。"""
    # 超过 6 张时只取前 6 张，避免布局超出当前设计范围。
    selected_paths = image_paths[:6]
    template = load_template(theme)
    canvas = _create_canvas(template)

    photo_boxes = get_image_layout(
        image_count=len(selected_paths),
        canvas_width=CANVAS_SIZE[0],
        image_area_top=IMAGE_AREA_TOP,
        image_area_bottom=IMAGE_AREA_BOTTOM,
    )
    photo_frame_dir = _resolve_photo_frame_dir(
        template,
        theme,
        photo_frame_theme,
        no_photo_frame,
    )
    forced_photo_frame = bool(photo_frame_theme and photo_frame_theme.lower() not in {"random", "none"})
    photo_frame_probability = template.get("photo_frame_probability", 0.6)
    if not isinstance(photo_frame_probability, (int, float)):
        photo_frame_probability = 0.6

    for box in photo_boxes:
        photo_frame_path = None
        if photo_frame_dir and (forced_photo_frame or random.random() <= photo_frame_probability):
            photo_frame_path = choose_photo_frame(photo_frame_dir)

        _paste_cropped_image(
            canvas,
            selected_paths[box.index],
            box,
            filter_name,
            auto_enhance,
            photo_frame_path,
        )

    add_random_stickers(canvas, template, photo_boxes, sticker_theme=sticker_theme)

    # 标题和底部文案最后绘制，保证不会被贴纸遮挡。
    draw_centered_text(
        image=canvas,
        text=title or random_title(template),
        box=(0, 0, CANVAS_SIZE[0], TITLE_AREA_HEIGHT),
        fill=random_title_color(template),
        font_size=78,
        randomize_font=True,
    )

    draw_centered_text(
        image=canvas,
        text=subtitle or random_footer(template),
        box=(0, CANVAS_SIZE[1] - FOOTER_AREA_HEIGHT, CANVAS_SIZE[0], CANVAS_SIZE[1]),
        fill=random_subtitle_color(template),
        font_size=40,
        randomize_font=True,
    )

    draw_centered_text(
        image=canvas,
        text=random_english_slogan(template),
        box=(0, IMAGE_AREA_BOTTOM + 8, CANVAS_SIZE[0], CANVAS_SIZE[1] - FOOTER_AREA_HEIGHT - 4),
        fill=random_subtitle_color(template),
        font_size=34,
        prefer_english=True,
        randomize_font=True,
    )

    canvas = _apply_frame(canvas, template)

    # 确保输出目录存在，macOS 和 Windows 都可用。
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)
    return output_path


def render_collage(title: str, names: list[str], output_path: Path) -> Path:
    """兼容旧的后端调用，后续可以再替换成真正拼图逻辑。"""
    image_paths = [Path(name) for name in names]
    return render_class_record(image_paths=image_paths, output_path=output_path, title=title)
