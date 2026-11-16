"""Composite the Blender scene + 3D title + JAVA + BEDROCK badge -> deliver/ thumbnails."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
DELIVER = os.path.join(HERE, "..", "deliver")
FONT = os.path.join(HERE, "assets", "LuckiestGuy.ttf")

bg = Image.open(os.path.join(HERE, "assets", "scene3d.png")).convert("RGBA").resize((1920, 1080), Image.LANCZOS)
bg = ImageEnhance.Color(bg).enhance(1.15)
bg = ImageEnhance.Contrast(bg).enhance(1.06)

# left-side darkening so the title pops
shade = Image.new("L", bg.size, 0)
d = ImageDraw.Draw(shade)
for x in range(1100):
    d.line([(x, 0), (x, 1080)], fill=int(110 * (1 - x / 1100) ** 1.6))
bg = Image.composite(Image.new("RGBA", bg.size, (20, 8, 40, 255)), bg, shade)

title = Image.open(os.path.join(HERE, "assets", "title3d_crop.png")).convert("RGBA")
tw = 1040
title = title.resize((tw, int(title.height * tw / title.width)), Image.LANCZOS)
# soft dark drop shadow behind the title
sh = Image.new("RGBA", title.size, (0, 0, 0, 0))
sh.putalpha(title.getchannel("A").point(lambda a: int(a * 0.75)))
sh = sh.filter(ImageFilter.GaussianBlur(18))
tx, ty = 40, 70
bg.alpha_composite(sh, (tx + 14, ty + 22))
bg.alpha_composite(title, (tx, ty))

# JAVA + BEDROCK badge
f = ImageFont.truetype(FONT, 62)
label = "JAVA + BEDROCK"
d = ImageDraw.Draw(bg)
l, t, r, b = d.textbbox((0, 0), label, font=f)
pw, ph = r - l + 70, b - t + 44
bx, by = tx + (tw - pw) // 2, ty + title.height + 10
badge = Image.new("RGBA", (pw + 16, ph + 16), (0, 0, 0, 0))
bd = ImageDraw.Draw(badge)
bd.rounded_rectangle((8, 14, pw + 8, ph + 14), 26, fill=(6, 26, 46, 200))
bd.rounded_rectangle((0, 0, pw, ph), 26, fill=(6, 26, 46, 255), outline=(255, 255, 255, 255), width=6)
bd.text((35 - l, 22 - t + 2), label, font=f, fill=(255, 208, 64, 255))
bg.alpha_composite(badge, (bx, by))

out = bg.convert("RGB")
os.makedirs(DELIVER, exist_ok=True)
out.save(os.path.join(DELIVER, "TidesSMP_Thumbnail_V2_1920.png"))
out.resize((1280, 720), Image.LANCZOS).save(os.path.join(DELIVER, "TidesSMP_Thumbnail_V2_1280.png"))
out.resize((320, 180), Image.LANCZOS).save(os.path.join(HERE, "..", "analysis", "v2_320.png"))
print("ok")
