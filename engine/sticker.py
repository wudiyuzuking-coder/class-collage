import random
from pathlib import Path
from typing import Any, Optional

from PIL import Image

from engine.layout import ImageBox


ROOT_DIR = Path(__file__).resolve().parents[1]
STICKERS_ROOT = ROOT_DIR / "assets" / "stickers"
DEFAULT_RANDOM_STICKER_THEMES = ("cute", "school", "summer")


def _png_files(directory: Path) -> list[Path]:
    """读取目录下的 PNG 文件；目录不存在或为空时返回空列表。"""
    if not directory.exists() or not directory.is_dir():
        return []

    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() == ".png"
    )


def load_stickers(sticker_theme: str = "random") -> list[Path]:
    """根据贴纸主题读取贴纸路径。"""
    safe_theme = (sticker_theme or "random").lower()

    if safe_theme == "random":
        sticker_paths: list[Path] = []
        for theme in DEFAULT_RANDOM_STICKER_THEMES:
            sticker_paths.extend(_png_files(STICKERS_ROOT / theme))
        return sorted(sticker_paths)

    if safe_theme == "all":
        if not STICKERS_ROOT.exists() or not STICKERS_ROOT.is_dir():
            return []
        sticker_paths: list[Path] = []
        for directory in STICKERS_ROOT.iterdir():
            if directory.is_dir():
                sticker_paths.extend(_png_files(directory))
        return sorted(sticker_paths)

    return _png_files(STICKERS_ROOT / safe_theme)


def load_stickers_by_theme(
    theme_config: dict[str, Any],
    sticker_theme: Optional[str] = None,
) -> list[Path]:
    """按命令行参数或模板配置读取贴纸。"""
    if sticker_theme:
        return load_stickers(sticker_theme)

    sticker_dir_name = theme_config.get("sticker_dir", "random")
    if not isinstance(sticker_dir_name, str) or not sticker_dir_name:
        sticker_dir_name = "random"
    return load_stickers(sticker_dir_name)


def rotate_sticker_randomly(
    sticker: Image.Image,
    min_angle: int = -45,
    max_angle: int = 45,
) -> Image.Image:
    """随机旋转贴纸，expand=True 防止旋转后被裁切。"""
    angle = random.uniform(min_angle, max_angle)
    return sticker.rotate(
        angle,
        resample=Image.Resampling.BICUBIC,
        expand=True,
        fillcolor=(255, 255, 255, 0),
    )


def _sticker_count_range(theme_config: dict[str, Any]) -> tuple[int, int]:
    """从模板配置中读取贴纸数量范围。"""
    count_range = theme_config.get("sticker_count_range", [5, 7])
    if (
        not isinstance(count_range, list)
        or len(count_range) != 2
        or not all(isinstance(value, int) for value in count_range)
    ):
        return 5, 7

    min_count, max_count = count_range
    min_count = max(0, min_count)
    max_count = max(min_count, max_count)
    return min_count, max_count


def _overlaps(rect_a: tuple[int, int, int, int], rect_b: tuple[int, int, int, int]) -> bool:
    """判断两个矩形是否重叠。"""
    left_a, top_a, right_a, bottom_a = rect_a
    left_b, top_b, right_b, bottom_b = rect_b
    return not (
        right_a <= left_b
        or right_b <= left_a
        or bottom_a <= top_b
        or bottom_b <= top_a
    )


def _photo_center_rect(box: ImageBox) -> tuple[int, int, int, int]:
    """取照片中间区域，贴纸会避开这里，减少遮挡主体。"""
    inset_x = int(box.width * 0.24)
    inset_y = int(box.height * 0.24)
    return (
        box.x + inset_x,
        box.y + inset_y,
        box.x + box.width - inset_x,
        box.y + box.height - inset_y,
    )


def _find_sticker_position(
    canvas_size: tuple[int, int],
    sticker_size: tuple[int, int],
    photo_boxes: list[ImageBox],
    placed_rects: list[tuple[int, int, int, int]],
    rng: random.Random,
) -> Optional[tuple[int, int]]:
    """按旋转后的真实尺寸随机寻找贴纸位置。"""
    canvas_width, canvas_height = canvas_size
    sticker_width, sticker_height = sticker_size
    forbidden_rects = [_photo_center_rect(box) for box in photo_boxes]

    # 候选区域优先选择角落和边缘留白，并避开标题、英文祝福语和底部文案的中心区域。
    forbidden_rects.extend(
        [
            (220, 0, canvas_width - 220, 135),
            (240, 1170, canvas_width - 240, canvas_height),
        ]
    )
    candidate_areas = [
        (24, 24, 210, 150),
        (canvas_width - 210, 24, canvas_width - 24, 150),
        (24, 1185, 230, canvas_height - 18),
        (canvas_width - 230, 1185, canvas_width - 24, canvas_height - 18),
        (12, 170, 150, 460),
        (12, 470, 150, 820),
        (12, 830, 150, 1160),
        (canvas_width - 150, 170, canvas_width - 12, 460),
        (canvas_width - 150, 470, canvas_width - 12, 820),
        (canvas_width - 150, 830, canvas_width - 12, 1160),
        (170, 126, 390, 205),
        (canvas_width - 390, 126, canvas_width - 170, 205),
        (170, 370, 260, 1040),
        (canvas_width - 260, 370, canvas_width - 170, 1040),
        (260, 136, 420, 230),
        (canvas_width - 420, 136, canvas_width - 260, 230),
        (260, 1110, 420, 1228),
        (canvas_width - 420, 1110, canvas_width - 260, 1228),
    ]

    for attempt in range(360):
        area_order = candidate_areas[:]
        rng.shuffle(area_order)
        left, top, right, bottom = area_order[attempt % len(area_order)]
        if right - left < sticker_width or bottom - top < sticker_height:
            continue

        x = rng.randint(left, right - sticker_width)
        y = rng.randint(top, bottom - sticker_height)

        # 再做一次画布边界保护，防止旋转后尺寸较大导致越界。
        x = max(0, min(x, canvas_width - sticker_width))
        y = max(0, min(y, canvas_height - sticker_height))
        rect = (x, y, x + sticker_width, y + sticker_height)

        if any(_overlaps(rect, forbidden) for forbidden in forbidden_rects):
            continue
        if any(_overlaps(rect, placed) for placed in placed_rects):
            continue

        return x, y

    return None


def add_random_stickers(
    canvas: Image.Image,
    theme_config: dict[str, Any],
    photo_boxes: list[ImageBox],
    sticker_theme: Optional[str] = None,
    min_size: int = 60,
    max_size: int = 140,
) -> Image.Image:
    """随机添加贴纸；没有贴纸文件时不报错。"""
    sticker_paths = load_stickers_by_theme(theme_config, sticker_theme)
    if not sticker_paths:
        return canvas

    min_count, max_count = _sticker_count_range(theme_config)
    if max_count <= 0:
        return canvas

    rng = random.Random()
    sticker_count = min(rng.randint(min_count, max_count), len(sticker_paths))
    available_stickers = sticker_paths[:]
    rng.shuffle(available_stickers)
    placed_rects: list[tuple[int, int, int, int]] = []

    while len(placed_rects) < sticker_count and available_stickers:
        sticker_path = available_stickers.pop()
        sticker_size = rng.randint(min_size, max_size)

        try:
            with Image.open(sticker_path) as sticker:
                sticker = sticker.convert("RGBA")
                placed = False

                for scale in (1.0, 0.85, 0.76, 0.66):
                    candidate = sticker.copy()
                    scaled_size = max(min_size, int(sticker_size * scale))
                    candidate.thumbnail((scaled_size, scaled_size), Image.Resampling.LANCZOS)
                    candidate = rotate_sticker_randomly(candidate)

                    position = _find_sticker_position(
                        canvas_size=canvas.size,
                        sticker_size=candidate.size,
                        photo_boxes=photo_boxes,
                        placed_rects=placed_rects,
                        rng=rng,
                    )
                    if position is None:
                        continue

                    x, y = position
                    canvas.paste(candidate, (x, y), candidate)
                    placed_rects.append((x, y, x + candidate.width, y + candidate.height))
                    placed = True
                    break

                if not placed:
                    continue
        except OSError:
            # 单个贴纸损坏时跳过，不影响整张图片生成。
            continue

    return canvas


def _clamp_position(
    x: int,
    y: int,
    sticker_size: tuple[int, int],
    canvas_size: tuple[int, int],
) -> tuple[int, int]:
    """把贴纸坐标限制在画布范围内，避免旋转后越界。"""
    sticker_width, sticker_height = sticker_size
    canvas_width, canvas_height = canvas_size
    x = max(0, min(x, canvas_width - sticker_width))
    y = max(0, min(y, canvas_height - sticker_height))
    return x, y


def _single_image_edge_position(
    image_rect: tuple[int, int, int, int],
    sticker_size: tuple[int, int],
    canvas_size: tuple[int, int],
    rng: random.Random,
) -> tuple[int, int]:
    """单图模式：把贴纸放在照片边缘附近，而不是照片中心。"""
    image_left, image_top, image_right, image_bottom = image_rect
    sticker_width, sticker_height = sticker_size
    edge = rng.choice(("left", "right", "top", "bottom"))

    if edge == "left":
        x = image_left - sticker_width // 2
        y = rng.randint(image_top + 24, max(image_top + 24, image_bottom - sticker_height - 24))
    elif edge == "right":
        x = image_right - sticker_width // 2
        y = rng.randint(image_top + 24, max(image_top + 24, image_bottom - sticker_height - 24))
    elif edge == "top":
        x = rng.randint(image_left + 24, max(image_left + 24, image_right - sticker_width - 24))
        y = image_top + 8
    else:
        x = rng.randint(image_left + 24, max(image_left + 24, image_right - sticker_width - 24))
        y = image_bottom - sticker_height // 2

    return _clamp_position(x, y, sticker_size, canvas_size)


def add_single_image_edge_stickers(
    canvas: Image.Image,
    theme_config: dict[str, Any],
    image_rect: tuple[int, int, int, int],
    sticker_theme: Optional[str] = None,
    min_count: int = 3,
    max_count: int = 4,
    min_size: int = 64,
    max_size: int = 120,
) -> Image.Image:
    """单图模式贴纸：随机 3~4 个，放在照片四周边缘，不重复使用。"""
    sticker_paths = load_stickers_by_theme(theme_config, sticker_theme)
    if not sticker_paths:
        return canvas

    rng = random.Random()
    sticker_count = min(rng.randint(min_count, max_count), len(sticker_paths))
    available_stickers = sticker_paths[:]
    rng.shuffle(available_stickers)
    placed_rects: list[tuple[int, int, int, int]] = []

    while len(placed_rects) < sticker_count and available_stickers:
        sticker_path = available_stickers.pop()
        sticker_size = rng.randint(min_size, max_size)

        try:
            with Image.open(sticker_path) as sticker:
                sticker = sticker.convert("RGBA")
                sticker.thumbnail((sticker_size, sticker_size), Image.Resampling.LANCZOS)
                sticker = rotate_sticker_randomly(sticker)

                for _ in range(80):
                    x, y = _single_image_edge_position(
                        image_rect=image_rect,
                        sticker_size=sticker.size,
                        canvas_size=canvas.size,
                        rng=rng,
                    )
                    rect = (x, y, x + sticker.width, y + sticker.height)
                    if any(_overlaps(rect, placed) for placed in placed_rects):
                        continue

                    canvas.paste(sticker, (x, y), sticker)
                    placed_rects.append(rect)
                    break
        except OSError:
            continue

    return canvas
