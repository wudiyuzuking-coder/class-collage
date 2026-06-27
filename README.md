# ClassCollage

ClassCollage 是一个课堂照片一键拼接美化工具。把 2 到 6 张课堂照片放入 `input/`，运行命令后会生成一张适合发给家长的课堂记录图片。

当前版本是轻量级命令行工具，只依赖 Pillow，不包含前端、AI、人脸识别、OpenCV 等复杂能力。

## 功能

- 自动读取 `jpg`、`jpeg`、`png`、`webp` 图片
- 支持 2 到 6 张图片生成课堂记录图
- 超过 6 张时只取前 6 张
- 图片自动居中裁剪并填满布局区域
- 默认启用轻量自动优化
- 支持 `none`、`soft`、`vivid`、`warm`、`cool` 滤镜
- 支持圆角、白色边框、轻微阴影
- 支持多模板主题：`cute`、`school`、`art`、`summer`
- 支持主题贴纸、背景图、画布边框图
- 支持单张照片相框
- 支持中文字体和英文字体按文本内容随机选择
- 没有贴纸、字体、背景、边框、相框素材时也会自动回退，不报错

## 安装

建议使用 Python 3.9 或更高版本。

```bash
pip install -r requirements.txt
```

`requirements.txt` 只包含：

```text
pillow
```

## 基础使用

1. 把 2 到 6 张图片放到 `input/` 目录。
2. 在项目根目录运行：

```bash
python main.py
```

生成结果会保存到：

```text
output/result.png
```

如果 `input/` 或 `output/` 不存在，程序会自动创建。图片少于 2 张时会提示：

```text
请至少放入 2 张图片
```

## 命令行参数

示例：

```bash
python main.py --input input --output output/demo.png --title "今日表现" --subtitle "积极举手，认真听讲" --theme cute
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--input` | `input` | 输入图片文件夹 |
| `--output` | `output/result.png` | 输出图片路径 |
| `--title` | 模板随机标题 | 自定义顶部标题 |
| `--subtitle` | 模板随机文案 | 自定义底部文案 |
| `--theme` | `cute` | 模板主题名称 |
| `--layout` | `auto` | 图片布局名称 |
| `--sticker-theme` | `random` | 贴纸来源 |
| `--photo-frame-theme` | `random` | 单张照片相框来源 |
| `--no-photo-frame` | 无 | 强制关闭照片相框 |
| `--filter` | `soft` | 图片滤镜 |
| `--no-auto-enhance` | 无 | 关闭默认自动优化 |
| `--list-themes` | 无 | 查看当前可用模板 |
| `--list-layouts` | 无 | 查看当前可用图片布局 |

## 可用模板

当前内置 4 个模板：

- `cute`：可爱、柔和，适合幼儿园
- `school`：清爽、有学习感，适合小学或培训班
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

如果输入不存在的主题，程序会提示并回退到 `cute`。

## 图片布局

ClassCollage 目前只保留少量稳定布局，默认使用 `--layout auto`，程序会根据图片数量随机选择对应布局。

查看全部布局：

```bash
python main.py --list-layouts
```

当前布局：

- 2 张图：`staggered`、`top_bottom`
- 3 张图：`diagonal_left`、`diagonal_right`
- 4 张图：`grid_2x2`
- 5 张图：`left3_right2`
- 6 张图：`grid_2x3`

指定布局示例：

```bash
python main.py --layout staggered
python main.py --layout diagonal_left
python main.py --layout grid_2x3
```

布局规则补充：

- 4 张及以上图片时，不使用单张照片 PNG 相框，只保留圆角、白边和阴影。
- 4 张及以上图片时，每张照片卡片会随机倾斜 `-20°` 到 `20°`，让画面更活泼。
- 如果指定的布局不适用于当前图片数量，程序会提示并回退到自动布局。

## 图片美化与滤镜

默认情况下，程序会先对每张输入图片进行轻量自动优化，再应用滤镜并进入拼图流程。

自动优化内容包括：

- 根据图片亮度轻微提亮或压暗
- 根据灰度分布轻微提高对比度
- 根据色彩状态轻微提高饱和度
- 非常轻微锐化

所有调整都比较保守，目标是让课堂照片更自然、更明亮、更适合拼图展示。

关闭自动优化：

```bash
python main.py --no-auto-enhance
```

支持的滤镜：

- `none`：不处理
- `soft`：柔和自然，默认滤镜
- `vivid`：鲜艳明亮
- `warm`：温暖亲切
- `cool`：清爽偏冷

示例：

```bash
python main.py --filter warm
python main.py --theme summer --filter vivid
```

## 模板系统

模板配置放在 `templates/{theme}/config.json`。

每个模板包含：

- `name`：模板显示名称
- `background_colors`：背景颜色列表
- `title_colors`：标题颜色列表
- `subtitle_colors`：底部文案颜色列表
- `titles`：随机标题列表
- `subtitles`：随机底部文案列表
- `sticker_dir`：默认贴纸目录
- `sticker_count_range`：贴纸数量范围
- `background_dir`：背景图目录
- `frame_dir`：画布边框图目录
- `photo_frame_dir`：单张照片相框目录

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

如果模板文件不存在、字段缺失或 JSON 读取失败，程序会自动回退到内置默认模板。

## 字体

程序会优先读取 `assets/fonts/` 下的字体文件，支持：

- `.ttf`
- `.otf`
- `.ttc`

文本会根据内容自动选择字体：

- 中文标题和中文文案优先使用中文文件名的字体
- 英文装饰文案优先使用英文文件名的字体
- 如果字体缺失或读取失败，会回退到系统字体或 Pillow 默认字体

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

每个贴纸会随机旋转 `-45°` 到 `45°`，并尽量放在画布四周和空白区域。贴纸不会重复使用。如果没有贴纸素材，程序会跳过贴纸步骤。

推荐素材类型：

- `cute`：小熊、小兔、爱心、云朵、星星、花朵
- `school`：铅笔、书本、苹果、尺子、小黑板
- `art`：画笔、调色盘、颜料、蜡笔、小画板
- `summer`：太阳、西瓜、冰淇淋、海浪、椰树

## 背景图和画布边框

背景图目录：

```text
assets/backgrounds/cute/
assets/backgrounds/school/
assets/backgrounds/art/
assets/backgrounds/summer/
```

画布边框图目录：

```text
assets/frames/cute/
assets/frames/school/
assets/frames/art/
assets/frames/summer/
```

资源建议：

- 背景图建议使用柔和、低干扰、浅色系 PNG
- 画布边框图建议使用透明 PNG，四周装饰，不遮挡中间照片内容
- 如果没有资源文件，会自动回退，不影响程序运行

## 照片相框系统

照片相框用于装饰单张课堂照片，和整张画布边框不同，它会套在单张照片卡片外面。

相框素材目录：

```text
assets/
└── photo_frames/
    ├── cute/
    ├── school/
    ├── summer/
    ├── cartoon/
    ├── game/
    └── simple/
```

推荐使用透明 PNG，中间透明，四周为装饰边框。没有相框素材时，程序会自动跳过。

命令示例：

```bash
python main.py --photo-frame-theme cute
python main.py --photo-frame-theme cartoon
python main.py --photo-frame-theme game
python main.py --photo-frame-theme none
python main.py --no-photo-frame
```

注意：4 张及以上图片时，程序会自动关闭单张照片相框，因为照片会随机倾斜，相框容易造成视觉拥挤。

相框素材建议：

- `cute`：云朵相框、星星相框、花朵相框、彩虹相框
- `school`：纸张相框、铅笔相框、书本相框、黑板相框
- `summer`：海浪相框、太阳相框、西瓜相框、沙滩相框
- `cartoon`：卡通粗描边相框、糖果色相框、课堂记录装饰相框
- `game`：金色头像框、水晶头像框、奖章头像框、魔法星星头像框

## 项目结构

```text
class-collage/
├── assets/
│   ├── backgrounds/
│   ├── fonts/
│   ├── frames/
│   ├── photo_frames/
│   └── stickers/
├── engine/
│   ├── assets.py
│   ├── decorate.py
│   ├── filter.py
│   ├── frame.py
│   ├── layout.py
│   ├── render.py
│   ├── sticker.py
│   ├── template.py
│   └── text.py
├── input/
├── output/
├── templates/
├── main.py
├── requirements.txt
└── README.md
```

## 素材说明

本项目中的图片、贴纸、相框、背景、边框、字体等素材仅用于本地测试和功能演示。部分素材可能来自网络、AI 生成或临时测试文件，不代表已经具备可商用或可再分发授权。

如果将项目正式开源、发布或用于商业场景，请自行替换为拥有明确授权的素材，并保留对应的来源说明和许可信息。

## License

MIT
