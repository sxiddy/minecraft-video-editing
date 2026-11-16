"""v6 (deliver V3): rim-lit bigger hero, no crafting table, plated tagline - split-waterline thumbnail (HQ hero, cleaned server frames, FX)."""
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda n: os.path.join(HERE, "assets", n)
DELIVER = os.path.join(HERE, "..", "deliver")
W, H, WL = 1920, 1080, 600
rnd = random.Random(4)

import cv2
import numpy as np


def denoise(img, h=6):
    a = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    a = cv2.fastNlMeansDenoisingColored(a, None, h, h, 7, 21)
    return Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))


def clahe(img, clip=2.2, tiles=8):
    a = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2LAB)
    a[..., 0] = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tiles, tiles)).apply(a[..., 0])
    return Image.fromarray(cv2.cvtColor(a, cv2.COLOR_LAB2RGB))


def soft_glow(size, center, radius, color, strength):
    g = Image.new("L", size, 0)
    ImageDraw.Draw(g).ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), fill=255)
    g = g.filter(ImageFilter.GaussianBlur(radius * 0.6)).point(lambda v: int(v * strength))
    lay = Image.new("RGBA", size, color + (0,))
    lay.putalpha(g)
    return lay


# ------------------------------------------------------------- background (real server frames)
canvas = Image.new("RGBA", (W, H))
src = Image.open(A("srv_sunset.png")).convert("RGB")
# remove the small blurry far-away player so the crafting table is the one clear server prop
a = cv2.cvtColor(np.array(src), cv2.COLOR_RGB2BGR)
m = np.zeros(a.shape[:2], np.uint8)
m[450:700, 885:975] = 255
a = cv2.inpaint(a, m, 9, cv2.INPAINT_TELEA)
src = Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))
# V3: cover the floating crafting table (+ reflection) with a feathered patch of open horizon from its left
patch = src.crop((700, 420, 940, 760))
pm = Image.new("L", patch.size, 0)
ImageDraw.Draw(pm).rectangle((30, 30, patch.width - 30, patch.height - 30), fill=255)
src.paste(patch, (935, 420), pm.filter(ImageFilter.GaussianBlur(14)))
top = clahe(denoise(src.crop((0, 140, 1920, 140 + WL)), 7), 2.4)
top = ImageEnhance.Brightness(top).enhance(1.42)
top = ImageEnhance.Color(top).enhance(1.95)
top = ImageEnhance.Contrast(top).enhance(1.2)
top = ImageChops.screen(top, Image.new("RGB", top.size, (40, 12, 0))).convert("RGBA")
# sunset glow + rays from the horizon behind the hero
sun = (1560, WL - 160)
top.alpha_composite(soft_glow(top.size, sun, 560, (255, 150, 60), 0.5))
top.alpha_composite(soft_glow(top.size, sun, 200, (255, 225, 160), 0.85))
rays = Image.new("L", top.size, 0)
rd = ImageDraw.Draw(rays)
for k in range(26):
    ang = math.radians(180 + k * (180 / 26) + rnd.uniform(-2, 2))
    w2 = math.radians(rnd.uniform(1.2, 2.6))
    R = 2400
    rd.polygon([sun, (sun[0] + R * math.cos(ang - w2), sun[1] + R * math.sin(ang - w2)),
                (sun[0] + R * math.cos(ang + w2), sun[1] + R * math.sin(ang + w2))], fill=rnd.randint(25, 55))
rays = rays.filter(ImageFilter.GaussianBlur(14))
rl = Image.new("RGBA", top.size, (255, 200, 140, 0))
rl.putalpha(rays)
top.alpha_composite(rl)
canvas.alpha_composite(top, (0, 0))

bot = denoise(Image.open(A("srv_reef.png")).convert("RGB").crop((0, 560, 1920, 1080)), 6)
bot = clahe(bot, 2.6).resize((W, H - WL), Image.LANCZOS)
bot = ImageEnhance.Brightness(bot).enhance(1.8)
bot = ImageEnhance.Color(bot).enhance(2.3)
bot = ImageEnhance.Contrast(bot).enhance(1.25)
bot = ImageChops.screen(bot, Image.new("RGB", bot.size, (0, 34, 48)))
# depth: darker toward the bottom, brighter just under the surface
dg = Image.linear_gradient("L").resize(bot.size).point(lambda v: int(v * 0.55))
bot = Image.composite(Image.new("RGB", bot.size, (2, 22, 40)), bot, dg)
br = Image.linear_gradient("L").resize(bot.size).point(lambda v: max(0, int((255 - v) * 0.45) - 80))
bot = Image.composite(Image.new("RGB", bot.size, (120, 230, 240)), bot, br)
uw = Image.new("L", bot.size, 0)
ud = ImageDraw.Draw(uw)
for _ in range(11):
    x = rnd.randint(-200, W)
    ud.polygon([(x, 0), (x + 90, 0), (x + 330, bot.height), (x + 150, bot.height)], fill=rnd.randint(30, 70))
bot = Image.composite(Image.new("RGB", bot.size, (190, 255, 245)), bot, uw.filter(ImageFilter.GaussianBlur(30)))
canvas.paste(bot, (0, WL))

# ------------------------------------------------------------- hero rising out of the water
hero = Image.open(A("hero_v3.png")).convert("RGBA")
hero = hero.crop(hero.getbbox())
hh = 1440
hero = hero.resize((int(hero.width * hh / hero.height), hh), Image.LANCZOS)
hx, hy = 905, -385
ha = Image.new("L", (W, H), 0)
ha.paste(hero.getchannel("A"), (hx, hy))
# warm atmospheric glow behind the character (no hard outline)
gl = Image.new("RGBA", (W, H), (255, 140, 70, 0))
gl.putalpha(ha.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.65)))
canvas.alpha_composite(gl)
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
# V3 separation from the orange sky: dark outline + cyan rim on the silhouette edge
ol = Image.new("RGBA", (W, H), (6, 22, 48, 0))
ol.putalpha(ha.filter(ImageFilter.MaxFilter(15)))
layer.alpha_composite(ol)
layer.alpha_composite(hero, (hx, hy))
edge = ImageChops.subtract(ha, ImageChops.offset(ha, 7, 5)).filter(ImageFilter.GaussianBlur(1.5))
rim = Image.new("RGBA", (W, H), (150, 245, 255, 0))
rim.putalpha(edge.point(lambda v: min(255, int(v * 0.9))))
layer.alpha_composite(rim)
halo = Image.new("RGBA", (W, H), (120, 230, 255, 0))
halo.putalpha(ha.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.55)))
canvas.alpha_composite(halo.crop((0, 0, W, WL)), (0, 0))
canvas.alpha_composite(layer.crop((0, 0, W, WL)), (0, 0))
# submerged part: refraction wobble, teal absorption, fade with depth
under = np.array(layer.crop((0, WL, W, H)))
out = np.zeros_like(under)
for y in range(under.shape[0]):
    out[y] = np.roll(under[y], int(7 * math.sin(y / 9.0) + 4 * math.sin(y / 23.0)), axis=0)
under = Image.fromarray(out)
ua = under.getchannel("A")
tint = Image.blend(under.convert("RGB"), Image.new("RGB", under.size, (10, 140, 165)), 0.5)
fade = Image.linear_gradient("L").resize(under.size).point(lambda v: max(0, int(175 - v * 0.75)))
under = tint.convert("RGBA")
under.putalpha(ImageChops.multiply(ua, fade))
canvas.alpha_composite(under, (0, WL))

# ------------------------------------------------------------- waterline meniscus
band = Image.new("RGBA", (W, 80), (0, 0, 0, 0))
bd = ImageDraw.Draw(band)
pts = [(x, 40 + 7 * math.sin(x / 60.0) + 3 * math.sin(x / 19.0)) for x in range(0, W + 6, 6)]
bd.line([(x, y + 6) for x, y in pts], fill=(10, 90, 120, 200), width=10)
bd.line(pts, fill=(170, 250, 255, 255), width=9)
bd.line([(x, y - 3) for x, y in pts], fill=(255, 255, 255, 255), width=3)
canvas.alpha_composite(band.filter(ImageFilter.GaussianBlur(12)), (0, WL - 40))
canvas.alpha_composite(band.filter(ImageFilter.GaussianBlur(1.2)), (0, WL - 40))

# ------------------------------------------------------------- foam + splash at the waist
cols = np.where(np.array(ha.crop((0, WL - 5, W, WL + 5))).max(axis=0) > 0)[0]
x0, x1 = (int(cols.min()), int(cols.max())) if len(cols) else (1300, 1700)
foam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fd = ImageDraw.Draw(foam)
for _ in range(200):
    x = rnd.uniform(x0 - 160, x1 + 160)
    near = x0 - 40 < x < x1 + 40
    y = WL + rnd.gauss(0, 9) - (6 if near else 0)
    r = rnd.uniform(6, 22) * (1.3 if near else 0.7)
    fd.ellipse((x - r * 1.8, y - r * 0.6, x + r * 1.8, y + r * 0.6), fill=(240, 255, 255, rnd.randint(70, 190)))
canvas.alpha_composite(foam.filter(ImageFilter.GaussianBlur(3.5)))
spl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(spl)
for _ in range(110):   # droplets thrown up
    side = rnd.choice((x0 - 30, x1 + 30))
    x = side + rnd.gauss(0, 70)
    y = WL - abs(rnd.gauss(0, 90)) - 10
    if x0 + 30 < x < x1 - 30:
        continue
    r = rnd.uniform(3, 10)
    sd.ellipse((x - r, y - r * 1.3, x + r, y + r * 1.3), fill=(235, 255, 255, 230))
    sd.ellipse((x - r * 0.4, y - r * 0.9, x + r * 0.1, y - r * 0.4), fill=(255, 255, 255, 255))
canvas.alpha_composite(spl.filter(ImageFilter.GaussianBlur(0.8)))

# bubbles: shaded spheres, not outlines
bub = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bdd = ImageDraw.Draw(bub)
for _ in range(45):
    x = rnd.gauss((x0 + x1) / 2, 200)
    y = rnd.uniform(WL + 25, H - 60)
    r = rnd.uniform(5, 20) * (1.4 - (y - WL) / (H - WL))
    bdd.ellipse((x - r, y - r, x + r, y + r), fill=(160, 240, 255, 50), outline=(220, 255, 255, 200), width=max(2, int(r / 5)))
    bdd.ellipse((x - r * 0.55, y - r * 0.6, x - r * 0.1, y - r * 0.15), fill=(255, 255, 255, 230))
canvas.alpha_composite(bub.filter(ImageFilter.GaussianBlur(0.7)))

# vignette
vg = Image.new("L", (W, H), 0)
ImageDraw.Draw(vg).ellipse((-300, -250, W + 300, H + 250), fill=255)
vg = ImageChops.invert(vg.filter(ImageFilter.GaussianBlur(160))).point(lambda v: int(v * 0.8))
canvas = Image.composite(Image.new("RGBA", (W, H), (4, 8, 26, 255)), canvas, vg)

pad = Image.new("L", (W, H), 0)
ImageDraw.Draw(pad).ellipse((-420, -200, 1150, 1250), fill=255)
pad = pad.filter(ImageFilter.GaussianBlur(170)).point(lambda v: int(v * 0.3))
canvas = Image.composite(Image.new("RGBA", (W, H), (6, 14, 34, 255)), canvas, pad)

# ------------------------------------------------------------- pixel-block logo
GLYPH = {
    "T": ["######", "######", "..##..", "..##..", "..##..", "..##..", "..##.."],
    "I": ["####", ".##.", ".##.", ".##.", ".##.", ".##.", "####"],
    "D": ["#####.", "######", "##..##", "##..##", "##..##", "######", "#####."],
    "E": ["######", "######", "##....", "#####.", "##....", "######", "######"],
    "S": [".#####", "######", "##....", "######", "....##", "######", "#####."],
    "M": ["##...##", "###.###", "#######", "##.#.##", "##...##", "##...##", "##...##"],
    "P": ["#####.", "######", "##..##", "######", "#####.", "##....", "##...."],
}


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def pixel_word(word, b, c_top, c_bot, depth_col, outline_col):
    cols = []
    for ch in word:
        g = GLYPH[ch]
        for x in range(len(g[0])):
            cols.append([row[x] for row in g])
        cols.append(["."] * 7)
    cols.pop()
    w, h = len(cols) * b, 7 * b
    pad = b * 2
    depth = int(b * 0.55)
    img = Image.new("RGBA", (w + pad * 2 + depth, h + pad * 2 + depth), (0, 0, 0, 0))
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    for x, col in enumerate(cols):
        for y, v in enumerate(col):
            if v == "#":
                md.rectangle((pad + x * b, pad + y * b, pad + (x + 1) * b - 1, pad + (y + 1) * b - 1), fill=255)
    # thick outline + extruded depth
    ol = mask.filter(ImageFilter.MaxFilter(int(b * 0.5) | 1))
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
        t = min(1, max(0, (y - pad) / (7 * b)))
        c = lerp(c_top, c_bot, t)
        gd.line([(0, y), (img.width, y)], fill=c + (255,))
    # faint pixel checker so it still reads as Minecraft blocks
    chk = Image.new("L", img.size, 0)
    cd = ImageDraw.Draw(chk)
    for x in range(0, img.width, b // 2):
        for y in range(0, img.height, b // 2):
            if rnd.random() < 0.35:
                cd.rectangle((x, y, x + b // 2 - 1, y + b // 2 - 1), fill=28)
    grad = Image.composite(Image.new("RGBA", img.size, depth_col + (255,)), grad, chk)
    hi = ImageChops.subtract(mask, ImageChops.offset(mask, 0, e))
    lo = ImageChops.subtract(mask, ImageChops.offset(mask, 0, -e))
    grad = Image.composite(Image.new("RGBA", img.size, (255, 255, 255, 255)), grad, hi.point(lambda v: int(v * 0.75)))
    grad = Image.composite(Image.new("RGBA", img.size, depth_col + (255,)), grad, lo.point(lambda v: int(v * 0.7)))
    grad.putalpha(mask)
    img.alpha_composite(grad)
    return img


tides = pixel_word("TIDES", 27, (200, 255, 255), (20, 150, 235), (5, 50, 110), (6, 22, 48))
smp = pixel_word("SMP", 21, (255, 245, 150), (255, 160, 20), (120, 60, 0), (6, 22, 48))

# pixel trident behind the logo (the ocean's sword)
TRI = ["#...#...#", "#...#...#", "#...#...#", "##..#..##", ".#######.", "....#....", "....#...."] + ["....#...."] * 22
tb = 20
tri = Image.new("RGBA", (9 * tb + 16, len(TRI) * tb + 16), (0, 0, 0, 0))
tm = Image.new("L", tri.size, 0)
tmd = ImageDraw.Draw(tm)
for y, row in enumerate(TRI):
    for x, v in enumerate(row):
        if v == "#":
            tmd.rectangle((8 + x * tb, 8 + y * tb, 8 + (x + 1) * tb - 1, 8 + (y + 1) * tb - 1), fill=255)
to = Image.new("RGBA", tri.size, (6, 22, 48, 255))
to.putalpha(tm.filter(ImageFilter.MaxFilter(9)))
tri.alpha_composite(to)
td = ImageDraw.Draw(tri)
for y, row in enumerate(TRI):
    for x, v in enumerate(row):
        if v == "#":
            c = (255, 210, 70) if y < 5 else ((40, 200, 190) if (y % 3) else (25, 140, 150))
            td.rectangle((8 + x * tb, 8 + y * tb, 8 + (x + 1) * tb - 1, 8 + (y + 1) * tb - 1), fill=c + (255,))
            td.rectangle((8 + x * tb, 8 + y * tb, 8 + (x + 1) * tb - 1, 8 + y * tb + 2), fill=(255, 255, 230, 255))

lx, ly = 60, 40
logo_w = tides.width
tri_x = lx + logo_w // 2 - tri.width // 2 - 10
canvas.alpha_composite(tri, (tri_x, ly - 40))
glow = Image.new("RGBA", tides.size, (120, 240, 255, 0))
glow.putalpha(tides.getchannel("A").filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.7)))
canvas.alpha_composite(glow, (lx, ly + 70))
canvas.alpha_composite(tides, (lx, ly + 70))
canvas.alpha_composite(smp, (lx + (logo_w - smp.width) // 2, ly + 70 + tides.height - 40))

# ------------------------------------------------------------- one plain line + small badge
F = "C:/Windows/Fonts/ariblk.ttf"
d = ImageDraw.Draw(canvas)
f = ImageFont.truetype(F, 74)
line = "OFFICIAL TRAILER"
bb = d.textbbox((0, 0), line, font=f)
tw_, th_ = bb[2] - bb[0], bb[3] - bb[1]
px0 = lx + (logo_w - tw_) // 2 - 34
py0 = WL + 70
plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
pd = ImageDraw.Draw(plate)
pd.rounded_rectangle((px0 + 8, py0 + 12, px0 + tw_ + 76, py0 + th_ + 60), 22, fill=(0, 6, 18, 170))
pd.rounded_rectangle((px0, py0, px0 + tw_ + 68, py0 + th_ + 48), 22, fill=(4, 14, 34, 235), outline=(255, 210, 70, 255), width=5)
canvas.alpha_composite(plate)
d = ImageDraw.Draw(canvas)
d.text((px0 + 34 - bb[0], py0 + 24 - bb[1]), line, font=f, fill=(255, 255, 255))
fb = ImageFont.truetype(F, 51)
label = "JAVA + BEDROCK"
bb = d.textbbox((0, 0), label, font=fb)
pw, ph = bb[2] - bb[0] + 66, bb[3] - bb[1] + 39
bx, by = px0 + (tw_ + 68 - pw) // 2, py0 + th_ + 48 + 26
d.rounded_rectangle((bx + 6, by + 9, bx + pw + 6, by + ph + 9), 24, fill=(0, 6, 18, 180))
d.rounded_rectangle((bx, by, bx + pw, by + ph), 24, fill=(6, 22, 48, 240), outline=(255, 210, 70), width=6)
d.text((bx + 33 - bb[0], by + 19 - bb[1]), label, font=fb, fill=(255, 255, 255))

out = canvas.convert("RGB")
# final finish: bloom on highlights, crisp sharpening, slight teal/orange split tone
hl = out.point(lambda v: max(0, v - 205) * 3).filter(ImageFilter.GaussianBlur(28))
out = ImageChops.screen(out, hl.point(lambda v: int(v * 0.55)))
out = out.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
out = ImageEnhance.Contrast(out).enhance(1.05)
os.makedirs(DELIVER, exist_ok=True)
out.save(os.path.join(DELIVER, "TidesSMP_Thumbnail_V3_1920.png"))
out.resize((1280, 720), Image.LANCZOS).save(os.path.join(DELIVER, "TidesSMP_Thumbnail_V3_1280.png"))
out.resize((320, 180), Image.LANCZOS).save(os.path.join(HERE, "..", "analysis", "v6_320.png"))
print("ok", tides.size, smp.size)
