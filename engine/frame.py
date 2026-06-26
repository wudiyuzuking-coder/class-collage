import random
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw


ROOT_DIR = Path(__file__).resolve().parents[1]
PHOTO_FRAMES_ROOT = ROOT_DIR / "assets" / "photo_frames"
TRANSPARENT_THRESHOLD = 32


def load_photo_frames(frame_dir: str) -> list[Path]:
    """读取照片相框目录下的 PNG 文件；目录不存在时返回空列表。"""
    safe_dir = frame_dir or "cute"
    directory = PHOTO_FRAMES_ROOT / safe_dir
    if not directory.exists() or not directory.is_dir():
        return []

    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() == ".png"
    )


def apply_photo_frame(photo_card: Image.Image, frame_path: Path) -> Image.Image:
    """把透明 PNG 相框缩放到照片卡片尺寸，并叠加到最上层。"""
    try:
        with Image.open(frame_path) as frame:
            frame = frame.convert("RGBA").resize(photo_card.size, Image.Resampling.LANCZOS)
    except OSError:
        return photo_card

    window = _detect_frame_window(frame)
    if window is None:
        result = photo_card.convert("RGBA")
        result.alpha_composite(frame)
        return result

    result = Image.new("RGBA", photo_card.size, (255, 255, 255, 0))
    clipped_photo = Image.new("RGBA", photo_card.size, (255, 255, 255, 0))
    clipped_photo.paste(photo_card.convert("RGBA"))
    clipped_photo.putalpha(_window_mask(photo_card.size, window))
    result.alpha_composite(clipped_photo)
    result.alpha_composite(frame)
    return result


def _longest_segment(values: list[int]) -> Optional[tuple[int, int]]:
    """从连续索引中找最长区间，用来定位相框中间的透明窗口。"""
    if not values:
        return None

    best_start = best_end = values[0]
    start = previous = values[0]
    for value in values[1:]:
        if value == previous + 1:
            previous = value
            continue

        if previous - start > best_end - best_start:
            best_start, best_end = start, previous
        start = previous = value

    if previous - start > best_end - best_start:
        best_start, best_end = start, previous
    return best_start, best_end + 1


def _detect_frame_window(frame: Image.Image) -> Optional[tuple[int, int, int, int]]:
    """根据相框透明区域估算照片窗口，避免照片从相框外侧漏出来。"""
    alpha = frame.getchannel("A")
    width, height = frame.size
    pixels = alpha.load()

    row_candidates = []
    for y in range(int(height * 0.08), int(height * 0.92)):
        transparent_count = sum(
            1 for x in range(width) if pixels[x, y] < TRANSPARENT_THRESHOLD
        )
        if transparent_count / width > 0.42:
            row_candidates.append(y)

    column_candidates = []
    for x in range(int(width * 0.08), int(width * 0.92)):
        transparent_count = sum(
            1 for y in range(height) if pixels[x, y] < TRANSPARENT_THRESHOLD
        )
        if transparent_count / height > 0.42:
            column_candidates.append(x)

    row_segment = _longest_segment(row_candidates)
    column_segment = _longest_segment(column_candidates)
    if row_segment is None or column_segment is None:
        return None

    left, right = column_segment
    top, bottom = row_segment
    if right - left < width * 0.35 or bottom - top < height * 0.25:
        return None

    # 向内收一点，避免照片边缘压到相框装饰线。
    inset = max(4, min(width, height) // 90)
    return (
        max(0, left + inset),
        max(0, top + inset),
        min(width, right - inset),
        min(height, bottom - inset),
    )


def _window_mask(size: tuple[int, int], window: tuple[int, int, int, int]) -> Image.Image:
    """为照片窗口创建圆角遮罩，让照片只显示在相框中间。"""
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    left, top, right, bottom = window
    radius = max(12, min(right - left, bottom - top) // 28)
    draw.rounded_rectangle(window, radius=radius, fill=255)
    return mask


def choose_photo_frame(frame_dir: str) -> Optional[Path]:
    """从指定相框主题中随机选择一个相框。"""
    frame_paths = load_photo_frames(frame_dir)
    if not frame_paths:
        return None
    return random.choice(frame_paths)
