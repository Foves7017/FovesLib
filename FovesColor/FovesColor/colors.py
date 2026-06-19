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


def color_whell(split: int, s: int, l: int) -> list[tuple[int, int, int]]:
    """ 将色轮分为 split 等分，然后按给定的饱和度和亮度生成颜色 """
    return [hsl_to_rgb(int(i * 360 / split), s, l) for i in range(split)]