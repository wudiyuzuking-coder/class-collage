import random
from pathlib import Path
from typing import Any, Optional

from PIL import Image, ImageOps


ROOT_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT_DIR / "assets"


def _png_files(directory: Path) -> list[Path]:
    """读取目录下的 PNG 文件；目录不存在或为空时返回空列表。"""
    if not directory.exists() or not directory.is_dir():
        return []

    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() == ".png"
    )


def _load_random_image(directory: Path, size: tuple[int, int]) -> Optional[Image.Image]:
    """随机读取一张 PNG，并缩放裁剪到指定尺寸。"""
    image_paths = _png_files(directory)
    if not image_paths:
        return None

    image_path = random.choice(image_paths)
    try:
        with Image.open(image_path) as image:
            image = ImageOps.exif_transpose(image).convert("RGBA")
            return ImageOps.fit(
                image,
                size,
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
    except OSError:
        return None


def load_random_background_image(
    theme_config: dict[str, Any],
    size: tuple[int, int],
) -> Optional[Image.Image]:
    """根据模板配置读取随机背景图；失败时返回 None。"""
    if not theme_config.get("use_background_image", False):
        return None

    background_dir = theme_config.get("background_dir", "cute")
    if not isinstance(background_dir, str) or not background_dir:
        background_dir = "cute"

    return _load_random_image(ASSETS_DIR / "backgrounds" / background_dir, size)


def load_random_frame_image(
    theme_config: dict[str, Any],
    size: tuple[int, int],
) -> Optional[Image.Image]:
    """根据模板配置读取随机边框图；失败时返回 None。"""
    if not theme_config.get("use_frame_image", False):
        return None

    frame_dir = theme_config.get("frame_dir", "cute")
    if not isinstance(frame_dir, str) or not frame_dir:
        frame_dir = "cute"

    return _load_random_image(ASSETS_DIR / "frames" / frame_dir, size)
