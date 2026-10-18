from typing import overload

@overload
def color_lerp(color_start: tuple[int, int, int], color_target: tuple[int, int, int], value: float|int) -> tuple[int, int, int]:
    ...

@overload
def color_lerp(color_start: tuple[int, int, int], color_target: tuple[int, int, int], value: list[float|int]) -> list[tuple[int, int, int]]:
    ...

def color_lerp(color_start: tuple[int, int, int], color_target: tuple[int, int, int], value: float|int|list[float|int]) -> tuple[int, int, int]|list[tuple[int, int, int]]:
    """ 对颜色进行线性插值。如果指定了多个值，则会返回多个结果 """
    if isinstance(value, float|int):
        values = [value]
    elif isinstance(value, list):
        values = value

    results = []
    for k in values:
        k = max(0, min(1, k))
        results.append(tuple(
            round(a + (b - a) * k)
            for a, b in zip(color_start, color_target)
        ))

    if isinstance(value, (float, int)):
        return results[0]
    else:
        return results

def hsl_to_rgb(h: int, s: int, l: int) -> tuple[int, int, int]:
    """
    将HSL颜色转换为RGB颜色
    
    参数:
        h: 色相 (0-360)
        s: 饱和度 (0-100)
        l: 亮度 (0-100)
    
    返回:
        tuple[int, int, int]: RGB颜色值，每个分量范围0-255
    """
    # 将HSL值转换为0-1范围
    h_norm = h / 360.0
    s_norm = s / 100.0
    l_norm = l / 100.0
    
    # 如果饱和度为0，则是灰色
    if s_norm == 0:
        r = g = b = l_norm
    else:
        # 计算临时变量
        def hue_to_rgb(p: float, q: float, t: float) -> float:
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p
        
        q = l_norm * (1 + s_norm) if l_norm < 0.5 else l_norm + s_norm - l_norm * s_norm
        p = 2 * l_norm - q
        
        r = hue_to_rgb(p, q, h_norm + 1/3)
        g = hue_to_rgb(p, q, h_norm)
        b = hue_to_rgb(p, q, h_norm - 1/3)
    
    # 将RGB值转换为0-255范围并四舍五入
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))

def rgb_to_hsl(r: int, g: int, b: int) -> tuple[int, int, int]:
    # RGB 归一化到 0~1
    r_ = r / 255
    g_ = g / 255
    b_ = b / 255

    max_c = max(r_, g_, b_)
    min_c = min(r_, g_, b_)

    # Lightness
    l = (max_c + min_c) / 2

    # 灰色情况
    if max_c == min_c:
        h = 0
        s = 0
    else:
        delta = max_c - min_c

        # Saturation
        if l > 0.5:
            s = delta / (2 - max_c - min_c)
        else:
            s = delta / (max_c + min_c)

        # Hue
        if max_c == r_:
            h = (g_ - b_) / delta
            if g_ < b_:
                h += 6
        elif max_c == g_:
            h = (b_ - r_) / delta + 2
        else:
            h = (r_ - g_) / delta + 4

        h /= 6

    return (
        round(h * 360),
        round(s * 100),
        round(l * 100)
    ) 

def rgb_tuple_to_hex(rgb: tuple[int, int, int]|list[tuple[int, int, int]]) -> str|list[str]:
    """
    将RGB元组转换为十六进制颜色字符串，支持批量调用

    参数:
        rgb: RGB元组，每个分量范围0-255

    返回:
        str: 十六进制颜色字符串，例如'#RRGGBB'
    """
    if isinstance(rgb, list):
        return [f'#{i[0]:02x}{i[1]:02x}{i[2]:02x}' for i in rgb]
    else:
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'


def color_wheel(split: int, s: int, l: int) -> list[tuple[int, int, int]]:
    """ 将色轮分为 split 等分，然后按给定的饱和度和亮度生成颜色 """
    return [hsl_to_rgb(int(i * 360 / split), s, l) for i in range(split)]