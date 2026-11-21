"""从一张带棋盘格背景的 jpg 里抠出 logo，输出带透明通道的 png。

背景处理
--------
源图是「白 + 浅灰」相间的棋盘格（表示透明），不是真透明。
直接把它当方图用会看到一层灰格子，所以这里自己算 alpha：

    像素 = a * 蓝 + (1 - a) * 棋盘格

而蓝色分量满足 b - r ≈ 160（实测顶左 69/124/241 → 172，底右 96/145/248 → 152），
棋盘格满足 b - r ≈ 0，所以

    a ≈ (b - r) / 蓝的 (b - r)

这一步免费得到了**抗锯齿的边缘**：既不用拟合圆角曲线（生成图的圆角是
「连续曲率」的，用圆弧或超椭圆去拟都拟不准），也不用做形态学腐蚀膨胀。

字是白色的，b - r 同样接近 0，会被上面这一步误判成透明。
所以再补一次**从背景往里的洪水填充**：从 (0,0)（一定是棋盘格）灌水，
灌不到的区域就是被蓝色包住的空洞，也就是 CS 两个字母，补成不透明。

顺序有个坑：洪水填充的种子必须在**背景**上。如果先裁剪再填，
(0,0) 就落在 logo 本体上，填充方向整个反过来，字母会保持透明
（表现为深色背景上「CS」变成黑洞）。所以必须先在整图上算 alpha。

去白边
------
JPEG 把边缘像素和浅色背景混在一起，直接留用会在深色主题下出现一圈白晕。
按 a 反解出纯色即可： color = (observed - (1 - a) * 棋盘格) / a。

用法
----
    python tools/extract_logo.py <源图> [--out web/public] [--size 256]

需要 Pillow： pip install pillow
"""
import argparse
import os
import sys

from PIL import Image

# 蓝色分量的目标值。源图是 135deg 品牌渐变，b - r 在 150~175 之间波动，
# 取 160 折中；偏差只会让边缘 alpha 有极小偏移，肉眼不可见。
BLUE_DELTA = 160.0

# 棋盘格两种色调的平均值，用来反解纯色。实测浅格 ~233 深格 ~255。
BG = (240.0, 240.0, 242.0)

# 二值化阈值：大于它算「实心蓝」，小于它算「背景或字」。
THRESH = 128

# 噪声地板：JPEG 压缩会在棋盘格上产生 ±3 的 b - r 抖动，
# 除以 160 之后是 0.019 的 alpha，放大到 256 就是 5 —— 足以在深色背景上
# 显出一层「脏边」。低于这个值一律当全透明。
NOISE = 12.0


def compute_alpha(im):
    """算出整张图的 alpha 图（255 = 完全不透明）。先在整图上做，别裁剪。"""
    w, h = im.size
    px = im.load()

    alpha = Image.new('L', (w, h))
    ap = alpha.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            d = b - r
            if d <= NOISE:
                ap[x, y] = 0
            else:
                a = d / BLUE_DELTA
                ap[x, y] = 255 if a >= 1 else int(a * 255)

    # 洪水填充：从**图像边界**灌水，灌不到的地方 = 被蓝色包住的空洞 = 白色字母
    #
    # 两个关键点，都是踩过的坑：
    # 1) 种子必须是「边界上的背景像素」，不能把图内所有低 alpha 像素都当成种子。
    #    白色字母的 b - r 同样接近 0（和棋盘格一样），如果图内所有低 alpha 像素
    #    都预置为可达，字母会一开始就算「reachable」，空洞检测完全失效。
    # 2) 自己写 BFS 而不用 PIL.ImageDraw.floodfill：后者逐像素重取参照色，
    #    同色块之间会串色，实测把 23 万个背景像素一起灌成了空洞。
    from collections import deque
    reach = bytearray(w * h)          # 1 = 能从图像边界走到（即真正的背景）

    def seed(x, y):
        i = y * w + x
        if not reach[i] and ap[x, y] < THRESH:
            reach[i] = 1
            queue.append(i)

    queue = deque()
    for x in range(w):
        seed(x, 0)
        seed(x, h - 1)
    for y in range(h):
        seed(0, y)
        seed(w - 1, y)

    while queue:
        i = queue.popleft()
        y, x = divmod(i, w)
        if x > 0:
            j = i - 1
            if not reach[j] and ap[x - 1, y] < THRESH:
                reach[j] = 1; queue.append(j)
        if x < w - 1:
            j = i + 1
            if not reach[j] and ap[x + 1, y] < THRESH:
                reach[j] = 1; queue.append(j)
        if y > 0:
            j = i - w
            if not reach[j] and ap[x, y - 1] < THRESH:
                reach[j] = 1; queue.append(j)
        if y < h - 1:
            j = i + w
            if not reach[j] and ap[x, y + 1] < THRESH:
                reach[j] = 1; queue.append(j)

    holes = 0
    for y in range(h):
        for x in range(w):
            i = y * w + x
            # 到不了背景、又不够实心 = 被蓝色包住的白色字母
            if not reach[i] and ap[x, y] < 255:
                ap[x, y] = 255
                holes += 1
    return alpha, holes


def find_box(im, alpha):
    """找出圆角方块的紧包围盒。

    不用「蓝色像素的极值」当边界 —— 抗锯齿的最外一圈是半透明的淡蓝，
    会被漏掉，裁出来边上有 1~2px 的白边。这里按 ~50% 覆盖率判定。
    """
    w, h = im.size
    ap = alpha.load()

    cols = {}
    for x in range(w):
        t = b_ = None
        for y in range(h):
            if ap[x, y] >= THRESH:
                if t is None:
                    t = y
                b_ = y
        if t is not None:
            cols[x] = (t, b_)
    if not cols:
        raise SystemExit('没找到 logo：整张图都没有足够蓝的像素')
    xs = sorted(cols)
    x0, x1 = xs[0], xs[-1]
    y0 = min(cols[x][0] for x in xs)
    y1 = max(cols[x][1] for x in xs)
    return x0, y0, x1, y1


def unpremultiply(im, alpha):
    """按 alpha 反解纯色，消掉 JPEG 带来的白边。"""
    w, h = im.size
    src = im.load()
    ap = alpha.load()
    out = Image.new('RGBA', (w, h))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            a = ap[x, y]
            if a == 0:
                op[x, y] = (0, 0, 0, 0)
                continue
            af = a / 255.0
            # a 很小的时候反解会放大噪声，钳到 0.35 起算
            aa = max(af, 0.35)
            op[x, y] = (
                max(0, min(255, int((r - (1 - aa) * BG[0]) / aa))),
                max(0, min(255, int((g - (1 - aa) * BG[1]) / aa))),
                max(0, min(255, int((b - (1 - aa) * BG[2]) / aa))),
                a,
            )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', help='源图路径（jpg/png 都行）')
    ap.add_argument('--out', default=None, help='输出目录，默认 <项目>/web/public')
    ap.add_argument('--size', type=int, default=256, help='输出边长，默认 256')
    ap.add_argument('--name', default='logo', help='输出文件名（不含扩展名）')
    ap.add_argument(
        '--favicons', action='store_true',
        help='额外按 16/32/180 输出 favicon16/32/180.png（各自从源图直接缩放）')
    args = ap.parse_args()

    if not os.path.isfile(args.src):
        raise SystemExit('源图不存在：' + args.src)

    out_dir = args.out or os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web', 'public'))

    im = Image.open(args.src).convert('RGB')
    print('源图 %dx%d' % im.size)

    # 顺序要紧：先整图算 alpha（洪水填充的种子必须在背景上），再裁剪
    alpha, holes = compute_alpha(im)
    print('补白的字母像素：%d' % holes)

    x0, y0, x1, y1 = find_box(im, alpha)
    print('logo 包围盒 (%d, %d, %d, %d)  %dx%d' % (x0, y0, x1, y1, x1 - x0 + 1, y1 - y0 + 1))

    cropped = im.crop((x0, y0, x1 + 1, y1 + 1))
    crop_alpha = alpha.crop((x0, y0, x1 + 1, y1 + 1))

    # 原图包围盒往往不是正方形（生成图常有轻微比例偏差）。
    # 不拉伸变形 —— 补透明边成正方形，logo 在里面居中。
    logo = unpremultiply(cropped, crop_alpha)
    w, h = logo.size
    side = max(w, h)
    if (w, h) != (side, side):
        canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        canvas.paste(logo, ((side - w) // 2, (side - h) // 2))
        logo = canvas
        print('包围盒非正方形 %dx%d -> 补透明边成 %dx%d（不拉伸）' % (w, h, side, side))

    def emit(target_px, filename):
        """每次都从原始尺寸缩放，不复用上一步的结果 ——
        256 再缩到 32 是二次重采样，实测字母糊成一团（LANCZOS 救不回来）。"""
        out = logo.resize((target_px, target_px), Image.LANCZOS) if target_px != side else logo
        path = os.path.join(out_dir, filename + '.png')
        out.save(path, 'PNG', optimize=True)
        op = out.load()
        n = target_px
        corner = [op[0, 0][3], op[n - 1, 0][3], op[0, n - 1][3], op[n - 1, n - 1][3]]
        print('  %-14s %3dx%-3d %6d bytes  四角alpha=%s 中心alpha=%d'
              % (filename, n, n, os.path.getsize(path), corner, op[n // 2, n // 2][3]))

    emit(args.size, args.name)
    if args.favicons:
        # 各尺寸都从原始裁剪图独立缩放，避免二次重采样
        for px_ in (16, 32, 180):
            emit(px_, 'favicon%d' % px_)


if __name__ == '__main__':
    sys.exit(main())
