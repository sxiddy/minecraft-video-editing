"""Split-waterline thumbnail: real server frames (sunset surface / coral reef) + 3D diver + title."""
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda n: os.path.join(HERE, "assets", n)
DELIVER = os.path.join(HERE, "..", "deliver")
FONT = A("LuckiestGuy.ttf")
W, H, WL = 1920, 1080, 520   # waterline y

canvas = Image.new("RGBA", (W, H))

# surface: lone crafting-table block on the open ocean at sunset (Job #12)
top = Image.open(A("srv_sunset.png")).convert("RGB").crop((0, 60, 1920, 60 + WL))
top = ImageEnhance.Brightness(top).enhance(1.55)
top = ImageEnhance.Color(top).enhance(1.6)
top = ImageEnhance.Contrast(top).enhance(1.15)
warm = Image.new("RGB", top.size, (255, 140, 60))
top = Image.blend(top, ImageChops.multiply(top, warm), 0.0)
top = ImageChops.screen(top, Image.new("RGB", top.size, (40, 12, 0)))
canvas.paste(top, (0, 0))

# below: coral reef (Job #3), lifted and pushed toward glowing teal
bot = Image.open(A("srv_reef.png")).convert("RGB").crop((0, 520, 1920, 1080))
bot = bot.resize((W, H - WL), Image.LANCZOS)
bot = ImageEnhance.Brightness(bot).enhance(2.1)
bot = ImageEnhance.Color(bot).enhance(1.9)
bot = ImageEnhance.Contrast(bot).enhance(1.2)
bot = ImageChops.screen(bot, Image.new("RGB", bot.size, (0, 38, 52)))
# light rays from the surface
rays = Image.new("L", bot.size, 0)
rd = ImageDraw.Draw(rays)
rnd = random.Random(4)
for _ in range(9):
    x = rnd.randint(0, W)
    rd.polygon([(x, 0), (x + 70, 0), (x + 260, bot.height), (x + 120, bot.height)], fill=rnd.randint(30, 60))
rays = rays.filter(ImageFilter.GaussianBlur(25))
bot = Image.composite(Image.new("RGB", bot.size, (170, 255, 245)), bot, rays)
canvas.paste(bot, (0, WL))

# waterline: bright wavy surface band
band = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
bd = ImageDraw.Draw(band)
pts = [(x, 30 + 9 * math.sin(x / 55.0) + 4 * math.sin(x / 17.0)) for x in range(0, W + 8, 8)]
bd.line(pts, fill=(200, 255, 255, 255), width=7)
bd.line([(x, y + 7) for x, y in pts], fill=(60, 200, 230, 200), width=6)
glow = band.filter(ImageFilter.GaussianBlur(10))
canvas.alpha_composite(glow, (0, WL - 30))
canvas.alpha_composite(band, (0, WL - 30))

# diver crossing the waterline, with a splash of bubbles
diver = Image.open(A("diver.png")).convert("RGBA")
bbox = diver.getbbox()
diver = diver.crop(bbox)
dh = 760
diver = diver.resize((int(diver.width * dh / diver.height), dh), Image.LANCZOS)
dx, dy = 1180, 150
outline = Image.new("RGBA", diver.size, (255, 255, 255, 0))
outline.putalpha(diver.getchannel("A").filter(ImageFilter.MaxFilter(13)))
canvas.alpha_composite(outline.filter(ImageFilter.GaussianBlur(2)), (dx, dy))
canvas.alpha_composite(diver, (dx, dy))
bub = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bbd = ImageDraw.Draw(bub)
for _ in range(40):
    x, y, r = rnd.gauss(dx + 330, 170), rnd.uniform(WL + 10, WL + 380), rnd.uniform(5, 18)
    bbd.ellipse((x - r, y - r, x + r, y + r), outline=(230, 255, 255, 230), width=3)
canvas.alpha_composite(bub)

# title (existing 3D render), top-left
title = Image.open(A("title3d_crop.png")).convert("RGBA")
tw = 880
title = title.resize((tw, int(title.height * tw / title.width)), Image.LANCZOS)
sh = Image.new("RGBA", title.size, (0, 0, 0, 0))
sh.putalpha(title.getchannel("A").point(lambda a: int(a * 0.8)))
canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (52, 40))
canvas.alpha_composite(title, (36, 20))


def outlined(img, xy, text, size, fill, stroke=(6, 26, 46), sw=10, shadow=True):
    f = ImageFont.truetype(FONT, size)
    d = ImageDraw.Draw(img)
    if shadow:
        d.text((xy[0] + 8, xy[1] + 10), text, font=f, fill=(0, 10, 25, 200), stroke_width=sw, stroke_fill=(0, 10, 25, 200))
    d.text(xy, text, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return d.textbbox(xy, text, font=f, stroke_width=sw)


# hook line, underwater
outlined(canvas, (60, 660), "AN ENTIRE WORLD", 118, (255, 255, 255))
b = outlined(canvas, (60, 790), "OF WATER", 150, (90, 240, 255))

# JAVA + BEDROCK badge
f = ImageFont.truetype(FONT, 52)
label = "JAVA + BEDROCK"
d = ImageDraw.Draw(canvas)
l, t, r, bt = d.textbbox((0, 0), label, font=f)
pw, ph = r - l + 60, bt - t + 36
bx, by = 64, 965
d.rounded_rectangle((bx + 6, by + 10, bx + pw + 6, by + ph + 10), 22, fill=(0, 10, 25, 200))
d.rounded_rectangle((bx, by, bx + pw, by + ph), 22, fill=(6, 26, 46, 255), outline=(255, 255, 255), width=5)
d.text((bx + 30 - l, by + 18 - t + 2), label, font=f, fill=(255, 208, 64))

out = canvas.convert("RGB")
os.makedirs(DELIVER, exist_ok=True)
out.save(os.path.join(DELIVER, "TidesSMP_Thumbnail_V2_1920.png"))
out.resize((1280, 720), Image.LANCZOS).save(os.path.join(DELIVER, "TidesSMP_Thumbnail_V2_1280.png"))
out.resize((320, 180), Image.LANCZOS).save(os.path.join(HERE, "..", "analysis", "v3_320.png"))
print("ok")
