"""生成 favicon（svg / 32 / 180 三份），纯标准库实现（无 Pillow）。

设计：与站点顶栏 .logo-mark 一致的「CS」品牌图标 ——
      135deg 品牌渐变圆角方块 + 白色 CS 字样。
      渐变取自 src/styles/main.css 的 --grad-brand（#3b6ef6 → #6f9bff），
      这样地址栏图标和页面左上角 logo 是同一套视觉。

svg 与 png 由同一份几何描述（下面的常量）生成，不会出现「svg 是一个样、
png 是另一个样」。png 走 4x 超采样 + box downsample，边缘无锯齿。
"""
import math
import os
import struct
import zlib

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web', 'public')

BASE = 64          # 设计稿尺寸
SS = 4             # 超采样倍数
RADIUS = 16        # 圆角

# 与 main.css --grad-brand 一致：135deg #3b6ef6 → #6f9bff
GRAD_A = (0x3b, 0x6e, 0xf6)
GRAD_B = (0x6f, 0x9b, 0xff)

STROKE = 6.2       # 字母笔画粗细
HALF = STROKE / 2.0

# ---- 字形几何（64 坐标系，y 向下）----
# C：以 (22,32) 为心的开口圆环，开口朝右，上下各留 52° 缺口
C_CX, C_CY, C_R = 22.0, 32.0, 9.6
C_A0, C_A1 = 52.0, 308.0          # 沿 y 向下坐标系，52° → 308° 经过底部/左侧

# S：一条折线骨架，SVG 用 polyline（圆角连接），PNG 用「到各段的最小距离」，
# 两者视觉一致。骨架控制在 x 35~50 / y 21~43，加半宽后正好落在 32~53 / 18~46。
# 采样点给密一点，圆角连接才不会出现折角；两个末端各留一小段平直收口。
S_PATH = [
    (49.8, 24.6), (48.8, 21.6), (45.4, 19.8), (41.0, 20.4),
    (37.6, 23.0), (37.0, 26.8), (39.4, 29.6), (43.6, 31.4),
    (47.4, 33.6), (48.6, 37.0), (47.0, 40.8), (43.4, 43.4),
    (39.0, 43.6), (35.8, 41.0),
]


def rounded_rect_contains(w, h, r, px, py):
    """点 (px,py) 是否落在圆角矩形内。"""
    cx = min(max(px, r), w - r)
    cy = min(max(py, r), h - r)
    return (px - cx) ** 2 + (py - cy) ** 2 <= r * r


def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def arc_dist(px, py, cx, cy, r, a0, a1):
    """点到「开口圆弧」的最小距离。角度用 y 向下的坐标系，单位度。

    落在 [a0, a1] 区间内的点按 |到圆心距离 - r| 算；落在缺口里的点
    取到两个端点的较小距离 —— 相当于给圆弧补了两个圆头端帽。
    """
    ang = math.degrees(math.atan2(py - cy, px - cx)) % 360.0
    in_arc = a0 <= ang <= a1
    if in_arc:
        return abs(math.hypot(px - cx, py - cy) - r)
    ends = []
    for a in (a0, a1):
        rad = math.radians(a)
        ends.append(math.hypot(px - (cx + r * math.cos(rad)), py - (cy + r * math.sin(rad))))
    return min(ends)


def _fmt(v):
    """SVG 坐标保留两位小数就够了，省字节。"""
    return ('%.2f' % v).rstrip('0').rstrip('.')


def build_svg():
    """由同一份几何生成 svg，保证与 png 一致。"""
    a0 = math.radians(C_A0)
    a1 = math.radians(C_A1)
    sx, sy = C_CX + C_R * math.cos(a0), C_CY + C_R * math.sin(a0)
    ex, ey = C_CX + C_R * math.cos(a1), C_CY + C_R * math.sin(a1)

    pts = ' '.join('%s,%s' % (_fmt(x), _fmt(y)) for x, y in S_PATH)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">\n'
        '  <defs>\n'
        '    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">\n'
        '      <stop offset="0%%" stop-color="#3b6ef6"/>\n'
        '      <stop offset="100%%" stop-color="#6f9bff"/>\n'
        '    </linearGradient>\n'
        '  </defs>\n'
        '  <rect width="64" height="64" rx="%d" fill="url(#g)"/>\n'
        '  <g fill="none" stroke="#fff" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round">\n'
        '    <path d="M %s %s A %s %s 0 1 0 %s %s"/>\n'
        '    <polyline points="%s"/>\n'
        '  </g>\n'
        '</svg>\n'
    ) % (
        RADIUS, _fmt(STROKE),
        _fmt(sx), _fmt(sy), _fmt(C_R), _fmt(C_R), _fmt(ex), _fmt(ey),
        pts,
    )


def sample(px, py):
    """返回 (r,g,b,a)，坐标为设计稿坐标系（0..BASE）。"""
    if not rounded_rect_contains(BASE, BASE, RADIUS, px, py):
        return (0, 0, 0, 0)
    # 135deg 渐变：左上 → 右下，投影到 (1,1) 方向上
    t = (px + py) / (2.0 * BASE)
    t = min(1.0, max(0.0, t))
    bg = tuple(int(round(GRAD_A[i] + (GRAD_B[i] - GRAD_A[i]) * t)) for i in range(3))

    ink = arc_dist(px, py, C_CX, C_CY, C_R, C_A0, C_A1) <= HALF
    if not ink:
        for i in range(len(S_PATH) - 1):
            x1, y1 = S_PATH[i]
            x2, y2 = S_PATH[i + 1]
            if seg_dist(px, py, x1, y1, x2, y2) <= HALF:
                ink = True
                break
    return (255, 255, 255, 255) if ink else (bg[0], bg[1], bg[2], 255)


def render(size):
    """先按 SS 倍超采样渲染，再 box downsample 到 size。"""
    big = size * SS
    acc = [[0.0, 0.0, 0.0, 0.0] for _ in range(big * big)]
    scale = BASE / big
    for j in range(big):
        py = (j + 0.5) * scale
        row = j * big
        for i in range(big):
            r, g, b, a = sample((i + 0.5) * scale, py)
            c = acc[row + i]
            c[0] += r * a
            c[1] += g * a
            c[2] += b * a
            c[3] += a
    n = SS * SS
    px = bytearray()
    for j in range(size):
        px.append(0)  # PNG filter type 0
        for i in range(size):
            block = [acc[(j * SS + jj) * big + (i * SS + ii)] for jj in range(SS) for ii in range(SS)]
            ar = sum(c[3] for c in block)
            if ar <= 0:
                px += bytes((0, 0, 0, 0))
            else:
                px += bytes((
                    int(round(sum(c[0] for c in block) / ar)),
                    int(round(sum(c[1] for c in block) / ar)),
                    int(round(sum(c[2] for c in block) / ar)),
                    int(round(ar / n)),
                ))
    return bytes(px)


def chunk(tag, data):
    return (struct.pack('>I', len(data)) + tag + data
            + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF))


def write_png(path, size, raw):
    hdr = struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', hdr)
           + chunk(b'IDAT', zlib.compress(raw, 9))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


if __name__ == '__main__':
    pub = os.path.normpath(OUT_DIR)
    svg_path = os.path.join(pub, 'favicon.svg')
    svg = build_svg().encode('utf-8')
    with open(svg_path, 'wb') as f:
        f.write(svg)
    print('favicon.svg    %d bytes  %s' % (len(svg), svg_path))
    for s in (32, 180):
        p = os.path.join(pub, 'favicon%d.png' % s)
        size = write_png(p, s, render(s))
        print('favicon%d.png  %d bytes  %s' % (s, size, p))
