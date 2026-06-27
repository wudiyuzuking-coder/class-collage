import json
from copy import deepcopy
from pathlib import Path
from typing import Any


# 内置默认模板。外部模板不存在或读取失败时，会使用这份配置兜底。
DEFAULT_TEMPLATE: dict[str, Any] = {
    "name": "Cute",
    "background_colors": ["#FFF7E8", "#FDEFF4", "#EAF7FF", "#F3F8E8"],
    "title_colors": ["#FF7B8A", "#6AA9FF", "#FFB347"],
    "subtitle_colors": ["#666666", "#888888"],
    "titles": ["今日课堂记录", "快乐学习时光", "今日精彩瞬间", "成长小记"],
    "subtitles": [
        "今天也有认真学习哦～",
        "每一次努力都值得被记录",
        "课堂上的精彩瞬间",
        "继续加油，越来越棒！",
    ],
    "english_slogans": [
        "Blessings for your everyday!",
        "Happy happy everyday!",
        "Shine bright every day!",
        "Learning brings little joys!",
    ],
    "sticker_dir": "cute",
    "sticker_count_range": [5, 7],
    "background_dir": "cute",
    "frame_dir": "cute",
    "use_background_image": False,
    "use_frame_image": False,
    "photo_frame_dir": "cartoon",
    "use_photo_frame": False,
    "photo_frame_probability": 1.0,
}

ROOT_DIR = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT_DIR / "templates"


def _merge_with_default(config: dict[str, Any]) -> dict[str, Any]:
    """把模板配置和默认配置合并，避免缺少字段时程序报错。"""
    template = deepcopy(DEFAULT_TEMPLATE)
    for key, value in config.items():
        # 只接受非空列表、普通字符串和布尔值，防止坏配置覆盖默认值。
        if isinstance(value, list) and value:
            template[key] = value
        elif isinstance(value, str) and value:
            template[key] = value
        elif isinstance(value, bool):
            template[key] = value
        elif isinstance(value, (int, float)):
            template[key] = value
    return template


def _normalize_template(template: dict[str, Any], theme: str) -> dict[str, Any]:
    """补齐主题资源字段，并修正不合理的贴纸数量范围。"""
    if not isinstance(template.get("sticker_dir"), str) or not template["sticker_dir"]:
        template["sticker_dir"] = theme or "cute"
    if not isinstance(template.get("background_dir"), str) or not template["background_dir"]:
        template["background_dir"] = theme or "cute"
    if not isinstance(template.get("frame_dir"), str) or not template["frame_dir"]:
        template["frame_dir"] = theme or "cute"
    if not isinstance(template.get("photo_frame_dir"), str) or not template["photo_frame_dir"]:
        template["photo_frame_dir"] = theme or "cute"

    if not isinstance(template.get("use_background_image"), bool):
        template["use_background_image"] = False
    if not isinstance(template.get("use_frame_image"), bool):
        template["use_frame_image"] = False
    if not isinstance(template.get("use_photo_frame"), bool):
        template["use_photo_frame"] = False

    probability = template.get("photo_frame_probability")
    if not isinstance(probability, (int, float)):
        probability = 0.6
    template["photo_frame_probability"] = max(0.0, min(1.0, float(probability)))

    count_range = template.get("sticker_count_range")
    if (
        not isinstance(count_range, list)
        or len(count_range) != 2
        or not all(isinstance(value, int) for value in count_range)
    ):
        template["sticker_count_range"] = [5, 7]
        return template

    min_count, max_count = count_range
    min_count = max(0, min_count)
    max_count = max(min_count, max_count)
    template["sticker_count_range"] = [min_count, max_count]
    return template


def list_templates() -> list[str]:
    """扫描 templates/ 目录，返回包含 config.json 的模板名称。"""
    if not TEMPLATES_DIR.exists():
        return ["cute"]

    themes = sorted(
        path.name
        for path in TEMPLATES_DIR.iterdir()
        if path.is_dir() and (path / "config.json").is_file()
    )
    return themes or ["cute"]


def template_exists(theme: str = "cute") -> bool:
    """判断指定模板配置文件是否存在。"""
    safe_theme = theme or "cute"
    return (TEMPLATES_DIR / safe_theme / "config.json").is_file()


def load_template(theme: str = "cute") -> dict[str, Any]:
    """读取主题模板；读取失败时回退内置默认配置。"""
    safe_theme = theme or "cute"
    config_path = TEMPLATES_DIR / safe_theme / "config.json"

    if not config_path.exists():
        return _normalize_template(deepcopy(DEFAULT_TEMPLATE), safe_theme)

    try:
        with config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except (OSError, json.JSONDecodeError):
        return _normalize_template(deepcopy(DEFAULT_TEMPLATE), safe_theme)

    if not isinstance(config, dict):
        return _normalize_template(deepcopy(DEFAULT_TEMPLATE), safe_theme)

    return _normalize_template(_merge_with_default(config), safe_theme)
