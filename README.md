# ClassCollage

课堂照片一键拼接美化工具。把 1~6 张课堂照片放进 `input/`，运行命令后生成一张适合发给家长的课堂记录图片。

当前版本是一个轻量级命令行工具，只依赖 Pillow。

## 功能

- 自动读取 `jpg`、`jpeg`、`png`、`webp` 图片
- 支持 1~6 张图片自动布局
- 超过 6 张时只取前 6 张
- 图片自动居中裁剪
- 默认启用轻量自动优化
- 支持轻量图片滤镜
- 圆角、白色边框、轻微阴影
- 支持多个模板主题
- 背景颜色、标题颜色、文案颜色来自模板配置
- 标题和底部文案来自模板配置，也支持命令行覆盖
- 支持透明 PNG 贴纸
- 没有贴纸、没有字体、没有 `input/output/assets` 目录时也能正常运行

## 安装

建议使用 Python 3.9 或更高版本。

```bash
pip install -r requirements.txt
```

`requirements.txt` 里只包含：

```text
pillow
```

## 基础使用

1. 把 1~6 张图片放到 `input/` 目录。
2. 在项目根目录运行：

```bash
python main.py
```

生成结果会保存到：

```text
output/result.png
```

如果 `input/` 不存在，程序会自动创建。图片少于 1 张时，会提示：

```text
请至少放入 1 张图片
```

## 命令行参数

```bash
python main.py --input input --output output/demo.png --title "今日表现" --subtitle "积极举手，认真听讲" --theme cute
```

参数说明：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--input` | `input` | 输入图片文件夹 |
| `--output` | `output/result.png` | 输出图片路径 |
| `--title` | 模板随机标题 | 自定义顶部标题 |
| `--subtitle` | 模板随机文案 | 自定义底部文案 |
| `--theme` | `cute` | 模板主题名称 |
| `--sticker-theme` | `random` | 贴纸来源 |
| `--photo-frame-theme` | `random` | 单张照片相框来源 |
| `--no-photo-frame` | 无 | 强制关闭照片相框 |
| `--filter` | `soft` | 图片滤镜 |
| `--no-auto-enhance` | 无 | 关闭默认自动优化 |
| `--list-themes` | 无 | 查看当前可用模板 |

## 可用模板

当前内置 4 个模板：

- `cute`：可爱、柔和，适合幼儿园
- `school`：清爽、学习感，适合小学或培训班
- `art`：美术课、创意、彩色
- `summer`：暑假班、活泼、阳光

查看模板列表：

```bash
python main.py --list-themes
```

使用指定模板：

```bash
python main.py --theme art
```

如果输入不存在的主题，例如：

```bash
python main.py --theme unknown
```

程序会提示：

```text
未找到主题 unknown，已使用默认主题 cute
```

然后继续使用 `cute` 模板生成图片。

## 图片美化与滤镜

默认情况下，程序会先对每张输入图片进行轻量自动优化，然后再应用滤镜并进入拼图流程。

自动优化内容包括：

- 根据图片亮度轻微提亮或压暗
- 根据灰度分布轻微提高对比度
- 根据色彩状态轻微提高饱和度
- 非常轻微锐化

目标是让课堂照片更自然、更明亮、更适合拼图展示。所有调整都比较保守，不会做夸张处理。

如果不想启用自动优化，可以使用：

```bash
python main.py --no-auto-enhance
```

滤镜只使用 Pillow 做轻量增强，不使用 AI、美颜模型、人脸识别或 OpenCV。

支持的滤镜：

- `none`：不处理
- `soft`：柔和自然，默认滤镜
- `vivid`：鲜艳明亮
- `warm`：温暖亲切
- `cool`：清爽偏冷

使用示例：

```bash
python main.py --filter warm
python main.py --theme summer --filter vivid
```

如果传入未知滤镜，程序会提示并自动回退到 `soft`。

## 模板系统

模板配置放在 `templates/{theme}/config.json`。

每个模板包含：

- `name`：模板显示名称
- `background_colors`：背景颜色列表
- `title_colors`：标题颜色列表
- `subtitle_colors`：底部文案颜色列表
- `titles`：随机标题列表
- `subtitles`：随机底部文案列表

目录示例：

```text
templates/
├── cute/
│   └── config.json
├── school/
│   └── config.json
├── art/
│   └── config.json
└── summer/
    └── config.json
```

如果模板文件不存在、字段缺失或 JSON 读取失败，程序会自动回退到内置默认模板，不会崩溃。

模板还可以配置贴纸目录和贴纸数量：

```json
{
  "sticker_dir": "cute",
  "sticker_count_range": [5, 7]
}
```

`sticker_dir` 会对应到 `assets/stickers/{sticker_dir}/`。

模板还可以配置背景图和边框图：

```json
{
  "background_dir": "cute",
  "frame_dir": "cute",
  "use_background_image": true,
  "use_frame_image": true
}
```

- `background_dir` 会对应到 `assets/backgrounds/{background_dir}/`
- `frame_dir` 会对应到 `assets/frames/{frame_dir}/`
- `use_background_image` 为 `true` 时，优先尝试使用背景图
- `use_frame_image` 为 `true` 时，优先尝试使用边框图
- 如果资源不存在或读取失败，会自动回退，不影响程序运行

## 项目结构

```text
class-collage/
├── assets/
│   ├── backgrounds/    按主题分类的背景图
│   ├── fonts/          可选字体目录
│   ├── frames/         按主题分类的透明边框图
│   └── stickers/       按主题分类的透明 PNG 贴纸
├── engine/
│   ├── decorate.py     圆角、边框、阴影
│   ├── layout.py       拼图布局
│   ├── render.py       画布渲染
│   ├── sticker.py      贴纸功能
│   ├── template.py     模板读取
│   └── text.py         文字绘制和字体
├── input/              输入图片
├── output/             输出图片
├── templates/          模板配置
├── main.py             命令行入口
├── requirements.txt
└── README.md
```

## 字体

程序会优先读取 `assets/fonts/` 下的字体文件，支持：

- `.ttf`
- `.otf`
- `.ttc`

如果没有自定义字体，会尝试使用系统中文字体。仍然找不到字体时，会回退到 Pillow 默认字体，程序不会报错。

文字会根据内容自动选择字体：中文标题和中文文案会从中文文件名的字体里随机选择，英文装饰文案会从英文文件名的字体里随机选择。中文不会使用只支持英文的装饰字体，防止被画成方块。

当前会在照片区下方随机显示一条英文祝福语：

- `Blessings for your everyday!`
- `Happy happy everyday!`
- `Shine bright every day!`
- `Learning brings little joys!`

## 主题贴纸

贴纸按主题放在不同目录里：

```text
assets/
└── stickers/
    ├── cute/
    ├── school/
    ├── art/
    └── summer/
```

每个目录里放透明 PNG 文件即可。对应关系由模板里的 `sticker_dir` 字段决定，例如：

```json
{
  "sticker_dir": "art"
}
```

表示这个模板会读取：

```text
assets/stickers/art/
```

推荐素材风格：

- `cute`：可爱风，如小熊、小兔、爱心、云朵、星星、花朵
- `school`：学习风，如铅笔、书本、苹果、尺子、小黑板
- `art`：美术风，如画笔、调色盘、颜料、蜡笔、小画板
- `summer`：夏日风，如太阳、西瓜、冰淇淋、海浪、椰树

程序会根据 `sticker_count_range` 随机选择贴纸数量，当前默认建议为 5~7 个，并尽量把贴纸放在画布四周和空白区域，避开照片中心、标题文案和英文祝福语。

如果某个主题的贴纸目录不存在或为空，程序会跳过贴纸，不会报错。

## 贴纸来源与旋转效果

默认情况下，程序会从以下主题中随机选择贴纸：

- `cute`
- `school`
- `summer`

默认不包含 `art`，因为美术贴纸更适合美术主题。

使用指定贴纸主题：

```bash
python main.py --sticker-theme cute
python main.py --sticker-theme school
python main.py --sticker-theme summer
python main.py --sticker-theme art
```

使用全部贴纸：

```bash
python main.py --sticker-theme all
```

继续使用默认随机贴纸：

```bash
python main.py --theme summer --sticker-theme random
```

每个贴纸会自动随机旋转 `-45°` 到 `45°`，让装饰效果更自然。旋转后会保留透明背景，并尽量避免越出画布。

## 主题背景图

背景图按主题放在不同目录里：

```text
assets/
└── backgrounds/
    ├── cute/
    ├── school/
    ├── art/
    └── summer/
```

背景图使用 PNG。建议使用柔和、低干扰、浅色系图片，避免影响照片和文字可读性。

如果没有背景图，或对应目录为空，程序会自动回退到模板中的随机纯色背景。

## 主题边框图

边框图按主题放在不同目录里：

```text
assets/
└── frames/
    ├── cute/
    ├── school/
    ├── art/
    └── summer/
```

边框图使用透明 PNG，建议做成四周装饰，不要遮挡中间照片内容。程序会把边框图缩放到 `1080x1350`，并作为最上层装饰覆盖到画布上。

如果没有边框图，或对应目录为空，程序会直接跳过，不会报错。

## 照片相框系统

照片相框用于装饰每一张课堂照片，和整张画布边框不同，它会套在单张照片卡片外面。

相框素材放在：

```text
assets/
└── photo_frames/
    ├── cute/
    ├── school/
    ├── summer/
    ├── game/
    └── simple/
```

推荐使用透明 PNG，相框中间透明，四周为装饰边框。如果没有相框素材，程序会自动跳过，不影响生成。

模板可以配置：

```json
{
  "photo_frame_dir": "cute",
  "use_photo_frame": true,
  "photo_frame_probability": 0.7
}
```

命令行示例：

```bash
python main.py --photo-frame-theme cute
python main.py --photo-frame-theme game
python main.py --photo-frame-theme none
python main.py --no-photo-frame
python main.py --theme summer --photo-frame-theme game
```

相框素材建议：

- `cute`：云朵相框、星星相框、花朵相框、彩虹相框
- `school`：纸张相框、铅笔相框、书本相框、黑板相框
- `summer`：海浪相框、太阳相框、西瓜相框、沙滩相框
- `game`：金色头像框、水晶头像框、奖章头像框、魔法星星头像框

## 素材说明

本项目中的图片、贴纸、相框、背景、边框、字体等素材仅用于本地测试和功能演示。部分素材可能来自网络、AI 生成或临时测试文件，不代表已经具备可商用或可再分发授权。

如果将项目正式开源、发布或用于商业场景，请自行替换为拥有明确授权的素材，并保留对应的来源说明和许可信息。

字体使用规则：

- `assets/fonts/` 中中文文件名的字体优先用于中文标题和中文文案。
- `assets/fonts/` 中英文文件名的字体优先用于英文装饰文案。
- 如果字体缺失或读取失败，程序会自动回退到系统字体或 Pillow 默认字体。

## License

MIT
