"""Critical SMP survival thumbnail: 4K plate (20 s savanna sunset) + Blender scene render + pixel logo + one line.

python compose_crit.py [scene.png]
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda n: os.path.join(HERE, "assets", n)
DELIVER = os.path.join(HERE, "..", "..", "deliver", "critical")
PLATE = "C:/Users/Siddharth D/tides-work/surv/f/p20.0.png"
SCENE = sys.argv[1] if len(sys.argv) > 1 else A("scene_full.png")
W, H = 1920, 1080
rnd = random.Random(9)


def glow(size, center, radius, color, strength):
    g = Image.new("L", size, 0)
    ImageDraw.Draw(g).ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), fill=255)
    g = g.filter(ImageFilter.GaussianBlur(radius * 0.6)).point(lambda v: int(v * strength))
    lay = Image.new("RGBA", size, color + (0,))
    lay.putalpha(g)
    return lay


def vgrad(h0, h1, a0, a1):
    """vertical alpha ramp (W x H): a0 at row h0 -> a1 at row h1, clamped."""
    y = np.arange(H, dtype=np.float32)
    t = np.clip((y - h0) / max(1, h1 - h0), 0, 1)
    col = (a0 + (a1 - a0) * t).astype(np.uint8)
    return Image.fromarray(np.repeat(col[:, None], W, axis=1))


# ------------------------------------------------------------- plate: 4K frame downsampled (sharp, no denoise)
plate = Image.open(PLATE).convert("RGB").resize((W, H), Image.LANCZOS)
# hide the tiny far-away player in the plate: feathered clone of the grass just to its right (small patch only)
_pm = Image.new("L", (170, 210), 0)
ImageDraw.Draw(_pm).rectangle((18, 18, 152, 192), fill=255)
plate.paste(plate.crop((710, 700, 880, 910)), (540, 700), _pm.filter(ImageFilter.GaussianBlur(8)))
plate = ImageEnhance.Contrast(plate).enhance(1.18)
plate = ImageEnhance.Color(plate).enhance(1.25)
plate = ImageEnhance.Brightness(plate).enhance(1.12)
canvas = plate.convert("RGBA")
# dusk: indigo/purple at the top of the sky so the warm logo + red hero pop by colour contrast (LESSONS thumb-v4)
dusk = Image.new("RGBA", (W, H), (52, 26, 96, 0))
dusk.putalpha(vgrad(0, 470, 175, 0))
canvas.alpha_composite(dusk)
# low sun behind the hero (the plate already has rays there) - warm backlight
canvas.alpha_composite(glow((W, H), (1260, 470), 520, (255, 150, 60), 0.45))
canvas.alpha_composite(glow((W, H), (1260, 470), 190, (255, 215, 150), 0.55))
# darken the ground a touch so the hero/props own the brightness
ground = Image.new("RGBA", (W, H), (10, 6, 14, 0))
ground.putalpha(vgrad(620, 1080, 0, 120))
canvas.alpha_composite(ground)

# ------------------------------------------------------------- scene render (hero, creeper, props, shadows)
scene = Image.open(SCENE).convert("RGBA")
if scene.size != (W, H):
    scene = scene.resize((W, H), Image.LANCZOS)
sa = scene.getchannel("A")
# soft warm atmosphere behind the characters (no hard halo)
bh = Image.new("RGBA", (W, H), (255, 140, 70, 0))
bh.putalpha(sa.filter(ImageFilter.GaussianBlur(45)).point(lambda v: int(v * 0.35)))
canvas.alpha_composite(bh)
canvas.alpha_composite(scene)

# torch + furnace light spill onto the plate around them
arr = np.asarray(scene).astype(np.float32)
hot = (arr[..., 0] > 240) & (arr[..., 1] > 200) & (arr[..., 3] > 200)
hot[:, :880] = False; hot[:, 1180:] = False
ys, xs = np.nonzero(hot)          # torch flame only (furnace is further left)
emit_pts = list(zip(xs.tolist(), ys.tolist()))
torch_c = (int(np.median(xs)), int(np.median(ys))) if len(xs) else (1010, 600)
canvas.alpha_composite(glow((W, H), torch_c, 260, (255, 140, 40), 0.42))

# ------------------------------------------------------------- embers rising from the torch (scene-derived FX)
emb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ed = ImageDraw.Draw(emb)
for _ in range(38):
    x = torch_c[0] + rnd.gauss(0, 45)
    y = torch_c[1] - abs(rnd.gauss(0, 150)) - 30
    r = rnd.uniform(1.6, 4.2)
    a = rnd.randint(140, 255)
    ed.rectangle((x - r, y - r, x + r, y + r), fill=(255, rnd.randint(120, 200), 40, a))
canvas.alpha_composite(emb.filter(ImageFilter.GaussianBlur(5)))
canvas.alpha_composite(emb.filter(ImageFilter.GaussianBlur(0.6)))

# vignette
vg = Image.new("L", (W, H), 0)
ImageDraw.Draw(vg).ellipse((-320, -260, W + 320, H + 260), fill=255)
vg = ImageChops.invert(vg.filter(ImageFilter.GaussianBlur(170))).point(lambda v: int(v * 0.85))
canvas = Image.composite(Image.new("RGBA", (W, H), (10, 4, 16, 255)), canvas, vg)
# dark pad behind the logo/line for read
pad = Image.new("L", (W, H), 0)
ImageDraw.Draw(pad).ellipse((-460, -260, 1180, 720), fill=255)
pad = pad.filter(ImageFilter.GaussianBlur(170)).point(lambda v: int(v * 0.32))
canvas = Image.composite(Image.new("RGBA", (W, H), (14, 6, 22, 255)), canvas, pad)

# ------------------------------------------------------------- pixel-block logo (same family as the Tides V3 logo)
GLYPH = {
    "C": [".#####", "######", "##....", "##....", "##....", "######", ".#####"],
    "R": ["#####.", "######", "##..##", "#####.", "####..", "##.##.", "##..##"],
    "I": ["####", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    "T": ["######", "######", "..##..", "..##..", "..##..", "..##..", "..##.."],
    "A": [".####.", "######", "##..##", "######", "######", "##..##", "##..##"],
    "L": ["##....", "##....", "##....", "##....", "##....", "######", "######"],
    "S": [".#####", "######", "##....", "######", "....##", "######", "#####."],
    "M": ["##...##", "###.###", "#######", "##.#.##", "##...##", "##...##", "##...##"],
    "P": ["#####.", "######", "##..##", "######", "#####.", "##....", "##...."],
}


def ramp(stops, t):
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if t <= p1:
            u = (t - p0) / max(1e-6, p1 - p0)
            return tuple(int(c0[i] + (c1[i] - c0[i]) * u) for i in range(3))
    return stops[-1][1]


def pixel_word(word, b, stops, depth_col, outline_col):
    cols = []
    for ch in word:
        g = GLYPH[ch]
        for x in range(len(g[0])):
            cols.append([row[x] for row in g])
        cols.append(["."] * 7)
    cols.pop()
    w, h = len(cols) * b, 7 * b
    padp = b * 2
    depth = int(b * 0.6)
    img = Image.new("RGBA", (w + padp * 2 + depth, h + padp * 2 + depth), (0, 0, 0, 0))
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    for x, col in enumerate(cols):
        for y, v in enumerate(col):
            if v == "#":
                md.rectangle((padp + x * b, padp + y * b, padp + (x + 1) * b - 1, padp + (y + 1) * b - 1), fill=255)
    ol = mask.filter(ImageFilter.MaxFilter(int(b * 0.55) | 1))
    for k in range(depth, 0, -1):
        sh = Image.new("RGBA", img.size, outline_col + (255,))
        sh.putalpha(ImageChops.offset(ol, k, k))
        img.alpha_composite(sh)
    o = Image.new("RGBA", img.size, outline_col + (255,))
    o.putalpha(ol)
    img.alpha_composite(o)
    e = max(3, b // 4)
    grad = Image.new("RGBA", img.size)
    gd = ImageDraw.Draw(grad)
    for y in range(img.height):
        t = min(1, max(0, (y - padp) / (7 * b)))
        gd.line([(0, y), (img.width, y)], fill=ramp(stops, t) + (255,))
    chk = Image.new("L", img.size, 0)
    cd = ImageDraw.Draw(chk)
    for x in range(0, img.width, b // 2):
        for y in range(0, img.height, b // 2):
            if rnd.random() < 0.33:
                cd.rectangle((x, y, x + b // 2 - 1, y + b // 2 - 1), fill=30)
    grad = Image.composite(Image.new("RGBA", img.size, depth_col + (255,)), grad, chk)
    hi = ImageChops.subtract(mask, ImageChops.offset(mask, 0, e))
    lo = ImageChops.subtract(mask, ImageChops.offset(mask, 0, -e))
    grad = Image.composite(Image.new("RGBA", img.size, (255, 255, 255, 255)), grad, hi.point(lambda v: int(v * 0.75)))
    grad = Image.composite(Image.new("RGBA", img.size, depth_col + (255,)), grad, lo.point(lambda v: int(v * 0.7)))
    grad.putalpha(mask)
    img.alpha_composite(grad)
    return img


OUTL = (24, 6, 10)
crit = pixel_word("CRITICAL", 18, [(0, (255, 240, 150)), (0.45, (255, 150, 30)), (1, (214, 32, 28))], (110, 12, 10), OUTL)
smp = pixel_word("SMP", 20, [(0, (255, 255, 255)), (1, (165, 176, 196))], (60, 66, 84), OUTL)

# crossed pixel sword + pickaxe emblem behind "SMP" (survival badge, integrated into the logo)
SW = ["............ww", "...........wWw", "..........wWw.", ".........wWw..", "........wWw...", ".......wWw....",
      "..g...wWw.....", "...g.wWw......", "....gWw.......", ".....g........", "....h.g.......", "...h..........",
      "..h...........", ".g............"]
PK = ["...ccccc......", "..cCCCCCc.....", ".c.....hcc....", "......h..c....", ".....h...c....", "....h.....c...",
      "...h..........", "..h...........", ".h............", "h............."]
pal = {"w": (200, 208, 220), "W": (250, 252, 255), "g": (60, 56, 72), "h": (120, 80, 40), "c": (60, 200, 210), "C": (150, 245, 240)}


def sprite(grid, b, flip=False):
    gw, gh = len(grid[0]), len(grid)
    im = Image.new("RGBA", (gw * b + 16, gh * b + 16), (0, 0, 0, 0))
    m = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(m)
    d = ImageDraw.Draw(im)
    cells = []
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch != ".":
                xx = (gw - 1 - x) if flip else x
                cells.append((xx, y, pal[ch]))
                md.rectangle((8 + xx * b, 8 + y * b, 8 + (xx + 1) * b - 1, 8 + (y + 1) * b - 1), fill=255)
    o = Image.new("RGBA", im.size, OUTL + (255,))
    o.putalpha(m.filter(ImageFilter.MaxFilter(9)))
    im.alpha_composite(o)
    for xx, y, c in cells:
        d.rectangle((8 + xx * b, 8 + y * b, 8 + (xx + 1) * b - 1, 8 + (y + 1) * b - 1), fill=c + (255,))
        d.rectangle((8 + xx * b, 8 + y * b, 8 + (xx + 1) * b - 1, 8 + y * b + 2), fill=(255, 255, 255, 120))
    return im


lx, ly = 50, 46
crit_x = lx
canvas.alpha_composite(glow((W, H), (crit_x + crit.width // 2, ly + crit.height // 2 + 10), 380, (255, 120, 30), 0.30))
smp_x = crit_x + (crit.width - smp.width) // 2
smp_y = ly + crit.height - 46
sw_img = sprite(SW, 17)
pk_img = sprite(PK, 17, flip=True)
cx = smp_x + smp.width // 2
canvas.alpha_composite(crit, (crit_x, ly))
canvas.alpha_composite(smp, (smp_x, smp_y))

# ------------------------------------------------------------- one plain line (text element #2)
F = "C:/Windows/Fonts/ariblk.ttf"
f = ImageFont.truetype(F, 66)
line = "OFFICIAL TRAILER"
d = ImageDraw.Draw(canvas)
bb = d.textbbox((0, 0), line, font=f)
tw_, th_ = bb[2] - bb[0], bb[3] - bb[1]
pw, ph = tw_ + 64, th_ + 44
px0 = crit_x + 22
py0 = smp_y + smp.height - 30
plate_l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
pd = ImageDraw.Draw(plate_l)
pd.rounded_rectangle((px0 + 8, py0 + 10, px0 + pw + 8, py0 + ph + 10), 20, fill=(4, 0, 6, 170))
pd.rounded_rectangle((px0, py0, px0 + pw, py0 + ph), 20, fill=(22, 8, 16, 238), outline=(255, 150, 40, 255), width=5)
canvas.alpha_composite(plate_l)
d = ImageDraw.Draw(canvas)
d.text((px0 + 32 - bb[0], py0 + 22 - bb[1]), line, font=f, fill=(255, 255, 255))

# ------------------------------------------------------------- finish
out = canvas.convert("RGB")
hl = out.point(lambda v: max(0, v - 210) * 3).filter(ImageFilter.GaussianBlur(26))
out = ImageChops.screen(out, hl.point(lambda v: int(v * 0.5)))
out = out.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
out = ImageEnhance.Color(ImageEnhance.Contrast(out).enhance(1.06)).enhance(1.1)
os.makedirs(DELIVER, exist_ok=True)
out.save(os.path.join(DELIVER, "CriticalSMP_Thumbnail_1920.png"))
out.resize((1280, 720), Image.LANCZOS).save(os.path.join(DELIVER, "CriticalSMP_Thumbnail_1280.png"))
out.resize((320, 180), Image.LANCZOS).save(os.path.join(HERE, "assets", "check_320.png"))
print("ok torch", torch_c, "logo", crit.size, smp.size, "line plate", (px0, py0, pw, ph))
