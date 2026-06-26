import argparse
from pathlib import Path

from engine.filter import DEFAULT_FILTER, SUPPORTED_FILTERS
from engine.render import render_class_record
from engine.template import list_templates, template_exists


# 项目根目录，使用 pathlib 保证 Windows 和 macOS 都能正常处理路径。
ROOT_DIR = Path(__file__).resolve().parent

# 当前阶段支持读取的图片格式。
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="ClassCollage：课堂照片一键拼接美化工具"
    )
    parser.add_argument("--input", default="input", help="输入图片文件夹，默认 input")
    parser.add_argument(
        "--output",
        default="output/result.png",
        help="输出图片文件，默认 output/result.png",
    )
    parser.add_argument("--title", default=None, help="自定义顶部标题")
    parser.add_argument("--subtitle", default=None, help="自定义底部文案")
    parser.add_argument("--theme", default="cute", help="模板主题名称，默认 cute")
    parser.add_argument(
        "--sticker-theme",
        default="random",
        help="贴纸来源：random、all、cute、school、art、summer，默认 random",
    )
    parser.add_argument(
        "--photo-frame-theme",
        default="random",
        help="照片相框来源：random、none、cute、school、summer、game、simple",
    )
    parser.add_argument(
        "--no-photo-frame",
        action="store_true",
        help="强制关闭照片相框",
    )
    parser.add_argument(
        "--filter",
        default=DEFAULT_FILTER,
        help="图片滤镜：none、soft、vivid、warm、cool，默认 soft",
    )
    parser.add_argument(
        "--auto-enhance",
        dest="auto_enhance",
        action="store_true",
        default=True,
        help="启用轻量自动优化，默认开启",
    )
    parser.add_argument(
        "--no-auto-enhance",
        dest="auto_enhance",
        action="store_false",
        help="关闭轻量自动优化",
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="列出当前可用模板并退出",
    )
    return parser.parse_args()


def project_path(path_text: str) -> Path:
    """把相对路径转换为项目内路径，绝对路径则原样使用。"""
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def find_input_images(input_dir: Path) -> list[Path]:
    """读取输入目录下的图片路径。"""
    if input_dir.exists() and not input_dir.is_dir():
        raise NotADirectoryError(f"输入路径不是文件夹：{input_dir}")

    # 自动创建输入目录，首次运行 python main.py 也不会因为目录不存在而报错。
    input_dir.mkdir(parents=True, exist_ok=True)

    # 只读取当前目录下的图片文件，按文件名排序让输出结果稳定。
    return sorted(
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def print_available_themes() -> None:
    """打印当前可用模板列表。"""
    print("可用模板：")
    for theme in list_templates():
        print(f"- {theme}")


def normalize_cli_filter(filter_name: str) -> str:
    """校验命令行滤镜参数，未知滤镜回退 soft。"""
    safe_name = (filter_name or DEFAULT_FILTER).lower()
    if safe_name not in SUPPORTED_FILTERS:
        print(f"未识别的滤镜 {filter_name}，已使用默认滤镜 {DEFAULT_FILTER}")
        return DEFAULT_FILTER
    return safe_name


def main() -> None:
    """程序入口：读取参数、检查图片数量，并生成课堂记录图。"""
    args = parse_args()

    if args.list_themes:
        print_available_themes()
        return

    theme = args.theme or "cute"
    if not template_exists(theme):
        print(f"未找到主题 {theme}，已使用默认主题 cute")
        theme = "cute"

    filter_name = normalize_cli_filter(args.filter)
    input_dir = project_path(args.input)
    output_path = project_path(args.output)

    if output_path.exists() and output_path.is_dir():
        print(f"输出路径不能是文件夹：{output_path}")
        return
    if output_path.parent.exists() and not output_path.parent.is_dir():
        print(f"输出目录不是文件夹：{output_path.parent}")
        return

    try:
        image_paths = find_input_images(input_dir)
    except NotADirectoryError as error:
        print(error)
        return

    if len(image_paths) < 1:
        print("请至少放入 1 张图片")
        return

    result_path = render_class_record(
        image_paths=image_paths,
        output_path=output_path,
        title=args.title,
        subtitle=args.subtitle,
        theme=theme,
        filter_name=filter_name,
        auto_enhance=args.auto_enhance,
        sticker_theme=args.sticker_theme,
        photo_frame_theme=args.photo_frame_theme,
        no_photo_frame=args.no_photo_frame,
    )
    print(f"已生成图片：{result_path}")


if __name__ == "__main__":
    main()
