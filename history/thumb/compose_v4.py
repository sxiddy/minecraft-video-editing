"""v4: pixel-block logo + one plain line, hero rising out of the waterline over real server frames."""
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda n: os.path.join(HERE, "assets", n)
DELIVER = os.path.join(HERE, "..", "deliver")
W, H, WL = 1920, 1080, 600
rnd = random.Random(4)

# ------------------------------------------------------------- background (real server frames)
canvas = Image.new("RGBA", (W, H))
top = Image.open(A("srv_sunset.png")).convert("RGB").crop((0, 140, 1920, 140 + WL))
top = ImageEnhance.Brightness(top).enhance(1.6)
top = ImageEnhance.Color(top).enhance(1.7)
top = ImageEnhance.Contrast(top).enhance(1.15)
top = ImageChops.screen(top, Image.new("RGB", top.size, (45, 14, 0)))
canvas.paste(top, (0, 0))
bot = Image.open(A("srv_reef.png")).convert("RGB").crop((0, 560, 1920, 1080)).resize((W, H - WL), Image.LANCZOS)
bot = ImageEnhance.Brightness(bot).enhance(2.1)
bot = ImageEnhance.Color(bot).enhance(1.9)
bot = ImageEnhance.Contrast(bot).enhance(1.2)
bot = ImageChops.screen(bot, Image.new("RGB", bot.size, (0, 38, 52)))
rays = Image.new("L", bot.size, 0)
rd = ImageDraw.Draw(rays)
for _ in range(9):
    x = rnd.randint(0, W)
    rd.polygon([(x, 0), (x + 70, 0), (x + 260, bot.height), (x + 120, bot.height)], fill=rnd.randint(30, 60))
bot = Image.composite(Image.new("RGB", bot.size, (170, 255, 245)), bot, rays.filter(ImageFilter.GaussianBlur(25)))
canvas.paste(bot, (0, WL))

# ------------------------------------------------------------- hero rising out of the water
hero = Image.open(A("hero.png")).convert("RGBA")
hero = hero.crop(hero.getbbox())
hh = 1260
hero = hero.resize((int(hero.width * hh / hero.height), hh), Image.LANCZOS)
hx, hy = 990, -300
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rim = Image.new("RGBA", hero.size, (255, 230, 200, 0))
rim.putalpha(hero.getchannel("A").filter(ImageFilter.MaxFilter(11)))
layer.alpha_composite(rim.filter(ImageFilter.GaussianBlur(3)), (hx, hy))
layer.alpha_composite(hero, (hx, hy))
# below the surface: tint teal and fade
under = layer.crop((0, WL, W, H))
ua = under.getchannel("A")
tint = Image.blend(under.convert("RGB"), Image.new("RGB", under.size, (20, 150, 170)), 0.45)
fade = Image.linear_gradient("L").resize(under.size).point(lambda v: int(150 - v * 0.45))
under = tint.convert("RGBA")
under.putalpha(ImageChops.multiply(ua, fade))
layer.paste(under, (0, WL))
canvas.alpha_composite(layer)

# waterline band + ripples at the hero's waist
band = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
bd = ImageDraw.Draw(band)
pts = [(x, 30 + 8 * math.sin(x / 55.0) + 3 * math.sin(x / 17.0)) for x in range(0, W + 8, 8)]
bd.line(pts, fill=(205, 255, 255, 255), width=6)
canvas.alpha_composite(band.filter(ImageFilter.GaussianBlur(9)), (0, WL - 30))
canvas.alpha_composite(band, (0, WL - 30))
rp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rpd = ImageDraw.Draw(rp)
cx = hx + hero.width // 2
for i, rx in enumerate((220, 330, 450)):
    rpd.ellipse((cx - rx, WL - rx * 0.09, cx + rx, WL + rx * 0.09), outline=(230, 255, 255, 200 - i * 55), width=5)
for _ in range(30):
    x, y, r = rnd.gauss(cx, 160), rnd.uniform(WL + 20, WL + 330), rnd.uniform(5, 15)
    rpd.ellipse((x - r, y - r, x + r, y + r), outline=(230, 255, 255, 210), width=3)
canvas.alpha_composite(rp)

# vignette
vg = Image.new("L", (W, H), 0)
ImageDraw.Draw(vg).ellipse((-300, -250, W + 300, H + 250), fill=255)
vg = ImageChops.invert(vg.filter(ImageFilter.GaussianBlur(160))).point(lambda v: int(v * 0.75))
canvas = Image.composite(Image.new("RGBA", (W, H), (5, 10, 30, 255)), canvas, vg)

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
f = ImageFont.truetype(F, 112)
ty = ly + 70 + tides.height - 40 + smp.height + 10
for i, line in enumerate(("OFFICIAL", "TRAILER")):
    bb = d.textbbox((0, 0), line, font=f)
    x = lx + (logo_w - (bb[2] - bb[0])) // 2
    y = ty + i * 118
    d.text((x + 6, y + 9), line, font=f, fill=(0, 8, 25, 230), stroke_width=8, stroke_fill=(0, 8, 25, 230))
    d.text((x, y), line, font=f, fill=(255, 255, 255), stroke_width=6, stroke_fill=(6, 22, 48))
fb = ImageFont.truetype(F, 34)
label = "JAVA + BEDROCK"
bb = d.textbbox((0, 0), label, font=fb)
pw, ph = bb[2] - bb[0] + 44, bb[3] - bb[1] + 26
bx, by = W - pw - 36, 34
d.rounded_rectangle((bx, by, bx + pw, by + ph), 16, fill=(6, 22, 48, 235), outline=(255, 210, 70), width=4)
d.text((bx + 22 - bb[0], by + 13 - bb[1]), label, font=fb, fill=(255, 255, 255))

out = canvas.convert("RGB")
os.makedirs(DELIVER, exist_ok=True)
out.save(os.path.join(DELIVER, "TidesSMP_Thumbnail_V2_1920.png"))
out.resize((1280, 720), Image.LANCZOS).save(os.path.join(DELIVER, "TidesSMP_Thumbnail_V2_1280.png"))
out.resize((320, 180), Image.LANCZOS).save(os.path.join(HERE, "..", "analysis", "v4_320.png"))
print("ok", tides.size, smp.size, ty)
