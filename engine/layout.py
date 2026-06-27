import random
from dataclasses import dataclass


@dataclass(frozen=True)
class ImageBox:
    """单张图片在画布中的位置和大小。"""

    index: int
    x: int
    y: int
    width: int
    height: int


LayoutItem = dict[str, int]


# 画布中的图片内容区域：x=60~1020，y=150~1180，图片间距约 24px。
# id 从 1 开始，渲染时会转换成从 0 开始的图片索引。
LAYOUT_TEMPLATES: dict[int, dict[str, list[LayoutItem]]] = {
    2: {
        "staggered": [
            {"id": 1, "x": 60, "y": 180, "w": 610, "h": 470},
            {"id": 2, "x": 410, "y": 620, "w": 610, "h": 470},
        ],
        "top_bottom": [
            {"id": 1, "x": 60, "y": 150, "w": 960, "h": 540},
            {"id": 2, "x": 60, "y": 640, "w": 960, "h": 540},
        ],
    },
    3: {
        "diagonal_left": [
            {"id": 1, "x": 60, "y": 160, "w": 620, "h": 360},
            {"id": 2, "x": 400, "y": 470, "w": 620, "h": 360},
            {"id": 3, "x": 60, "y": 790, "w": 620, "h": 360},
        ],
        "diagonal_right": [
            {"id": 1, "x": 400, "y": 160, "w": 620, "h": 360},
            {"id": 2, "x": 60, "y": 470, "w": 620, "h": 360},
            {"id": 3, "x": 400, "y": 790, "w": 620, "h": 360},
        ],
    },
    4: {
        "grid_2x2": [
            {"id": 1, "x": 60, "y": 150, "w": 500, "h": 530},
            {"id": 2, "x": 520, "y": 150, "w": 500, "h": 530},
            {"id": 3, "x": 60, "y": 650, "w": 500, "h": 530},
            {"id": 4, "x": 520, "y": 650, "w": 500, "h": 530},
        ],
    },
    5: {
        "left3_right2": [
            {"id": 1, "x": 60, "y": 150, "w": 560, "h": 360},
            {"id": 2, "x": 60, "y": 470, "w": 560, "h": 360},
            {"id": 3, "x": 60, "y": 790, "w": 560, "h": 360},
            {"id": 4, "x": 540, "y": 220, "w": 480, "h": 520},
            {"id": 5, "x": 540, "y": 640, "w": 480, "h": 520},
        ],
    },
    6: {
        "grid_2x3": [
            {"id": 1, "x": 60, "y": 150, "w": 330, "h": 530},
            {"id": 2, "x": 375, "y": 150, "w": 330, "h": 530},
            {"id": 3, "x": 690, "y": 150, "w": 330, "h": 530},
            {"id": 4, "x": 60, "y": 650, "w": 330, "h": 530},
            {"id": 5, "x": 375, "y": 650, "w": 330, "h": 530},
            {"id": 6, "x": 690, "y": 650, "w": 330, "h": 530},
        ],
    },
}


def get_available_layouts(image_count: int) -> list[str]:
    """返回指定图片数量支持的布局名称。"""
    count = min(max(image_count, 2), 6)
    return list(LAYOUT_TEMPLATES.get(count, {}).keys())


def get_all_layouts() -> dict[int, list[str]]:
    """返回 2~6 张图片支持的全部布局名称，供命令行展示。"""
    return {count: get_available_layouts(count) for count in range(2, 7)}


def get_layout(image_count: int, layout_name: str = "auto") -> list[LayoutItem]:
    """按图片数量和布局名返回布局矩形；auto 会随机选择当前数量的布局。"""
    count = min(max(image_count, 2), 6)
    layout_group = LAYOUT_TEMPLATES.get(count, {})
    if not layout_group:
        return []

    safe_name = (layout_name or "auto").lower()
    if safe_name == "auto":
        safe_name = random.choice(get_available_layouts(count))
    elif safe_name not in layout_group:
        print(f"未找到适用于 {count} 张图片的布局 {layout_name}，已使用自动布局")
        safe_name = random.choice(get_available_layouts(count))

    # 返回复制后的 dict，避免调用方意外修改模板。
    return [dict(item) for item in layout_group[safe_name]]


def get_image_layout(
    image_count: int,
    canvas_width: int = 1080,
    image_area_top: int = 150,
    image_area_bottom: int = 1180,
    margin: int = 60,
    gap: int = 24,
    layout_name: str = "auto",
) -> list[ImageBox]:
    """兼容旧接口：返回 ImageBox 列表供 render.py 和 sticker.py 使用。"""
    del canvas_width, image_area_top, image_area_bottom, margin, gap

    boxes: list[ImageBox] = []
    for item in get_layout(image_count, layout_name):
        boxes.append(
            ImageBox(
                index=item["id"] - 1,
                x=item["x"],
                y=item["y"],
                width=item["w"],
                height=item["h"],
            )
        )
    return boxes
