from dataclasses import dataclass


@dataclass(frozen=True)
class ImageBox:
    """单张图片在画布中的位置和大小。"""

    index: int
    x: int
    y: int
    width: int
    height: int


def _row_layout(
    indexes: list[int],
    y: int,
    row_height: int,
    left: int,
    right: int,
    gap: int,
) -> list[ImageBox]:
    """计算一行图片的位置。"""
    count = len(indexes)
    total_width = right - left
    image_width = (total_width - gap * (count - 1)) // count

    boxes: list[ImageBox] = []
    for column, index in enumerate(indexes):
        x = left + column * (image_width + gap)
        boxes.append(ImageBox(index=index, x=x, y=y, width=image_width, height=row_height))
    return boxes


def get_image_layout(
    image_count: int,
    canvas_width: int = 1080,
    image_area_top: int = 150,
    image_area_bottom: int = 1180,
    margin: int = 60,
    gap: int = 24,
) -> list[ImageBox]:
    """根据图片数量返回 1~6 张图片的自动拼图布局。"""
    count = min(image_count, 6)
    if count < 1:
        return []

    # 每个子列表代表一行，数字代表对应第几张图片
    row_patterns: dict[int, list[list[int]]] = {
        1: [[0]],
        2: [[0], [1]],
        3: [[0], [1, 2]],
        4: [[0, 1], [2, 3]],
        5: [[0, 1], [2, 3, 4]],
        6: [[0, 1, 2], [3, 4, 5]],
    }
    rows = row_patterns[count]

    row_count = len(rows)
    available_height = image_area_bottom - image_area_top
    row_height = (available_height - gap * (row_count - 1)) // row_count

    boxes: list[ImageBox] = []
    for row_index, indexes in enumerate(rows):
        y = image_area_top + row_index * (row_height + gap)
        boxes.extend(
            _row_layout(
                indexes=indexes,
                y=y,
                row_height=row_height,
                left=margin,
                right=canvas_width - margin,
                gap=gap,
            )
        )

    return boxes
