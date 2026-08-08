# FovesColor
包括一系列和颜色相关的工具。

可使用 pip 安装或下载源码使用：
```BASH
pip install FovesColor
```

项目主页：
https://github.com/Foves7017/FovesLib


## `hsl_to_rgb(h, s, l)`

将 HSL 颜色转换为 RGB。

| 参数 | 类型 | 范围 | 说明 |
|------|------|------|------|
| `h` | `int` | 0–360 | 色相 |
| `s` | `int` | 0–100 | 饱和度 |
| `l` | `int` | 0–100 | 亮度 |

返回 `tuple[int, int, int]`，每个分量范围 0–255。

## `rgb_to_hsl(r, g, b)`

将 HSL 颜色转换为 RGB。

| 参数 | 类型 | 范围 | 说明 |
|------|------|------|------|
| `r` | `int` | 0-255 | 红色分量 |
| `g` | `int` | 0-255 | 绿色分量 |
| `b` | `int` | 0-255 | 蓝色分量 |

返回 `tuple[int, int, int]`， h 分量范围 0–255，s 和 l 分量范围 0-100

## `rgb_tuple_to_hex(rgb)`

将 RGB 元组转换为 `#RRGGBB` 十六进制字符串。**支持单个和批量**——传入列表自动返回列表。

| 参数 | 类型 | 说明 |
|------|------|------|
| `rgb` | `tuple[int,int,int]` | 单个 RGB 颜色 |
| `rgb` | `list[tuple[int,int,int]]` | 批量 RGB 颜色 |

返回 `str`（单个）或 `list[str]`（批量）。


## `color_whell(split, s, l)`

将色轮均分为 `split` 等份，按指定饱和度和亮度生成 RGB 颜色列表。

| 参数 | 类型 | 范围 | 说明 |
|------|------|------|------|
| `split` | `int` | ≥1 | 色轮分割份数 |
| `s` | `int` | 0–100 | 饱和度 |
| `l` | `int` | 0–100 | 亮度 |

返回 `list[tuple[int, int, int]]`。

# 更新日志

v0.2.0
 - 添加了 `rgb_to_hsl` 函数，可以将 RGB 颜色转换为 HSL
 - 添加了 `color_leap` 函数，可以线性插值颜色
