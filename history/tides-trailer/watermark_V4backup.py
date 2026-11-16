"""Client-preview watermark: heavy enough that the preview is unusable - dense 45% "MediaSynx" tiling, diagonal
grid lines, a big 65% "MediaSynx PREVIEW" plate in the centre and a drifting mark.
python watermark.py IN.mp4 OUT.mp4   |   python watermark.py IN.png OUT.png"""
import sys, subprocess, pathlib
from PIL import Image, ImageDraw, ImageFont
F = str(pathlib.Path(__file__).parent / "assets/fonts/cine/Manrope.ttf")
src, dst = sys.argv[1], sys.argv[2]

def bold(size):
    f = ImageFont.truetype(F, size); f.set_variation_by_axes([800]); return f
tile = pathlib.Path("C:/Users/Siddharth D/tides-work/wm_tile.png")
mark = pathlib.Path("C:/Users/Siddharth D/tides-work/wm_mark.png")

def text_img(size, alpha):
    f = bold(size); w = int(f.getlength("MediaSynx")) + 20
    im = Image.new("RGBA", (w, size + 30)); ImageDraw.Draw(im).text((10, 5), "MediaSynx", font=f, fill=(255, 255, 255, alpha))
    return im

def make_tile(W, H, heavy=True):
    big = Image.new("RGBA", (W * 2, H * 2)); t = text_img(int(H * 0.06), 115 if heavy else 62)
    d = ImageDraw.Draw(big)
    for y in range(0, H * 2, int(H * 0.11)):
        for x in range(-((y // int(H * 0.11)) % 2) * t.width // 2, W * 2, t.width + int(W * 0.02)):
            big.alpha_composite(t, (x, y))
        if heavy:
            d.line([(0, y - 6), (W * 2, y - 6)], fill=(255, 255, 255, 70), width=3)
    big = big.rotate(28, resample=Image.BICUBIC)
    out = big.crop((W // 2, H // 2, W // 2 + W, H // 2 + H))
    if not heavy:  # video: full-frame tiling only - watchable, but not uploadable
        return out
    od = ImageDraw.Draw(out)
    for k in range(-H, W, int(W * 0.12)):  # counter-diagonal lines
        od.line([(k, H), (k + H, 0)], fill=(0, 0, 0, 60), width=4)
    plate = Image.new("RGBA", (W, int(H * 0.30)), (0, 0, 0, 120))
    f = bold(int(H * 0.13)); txt = "MediaSynx  PREVIEW"
    ImageDraw.Draw(plate).text(((W - f.getlength(txt)) / 2, int(H * 0.06)), txt, font=f, fill=(255, 255, 255, 170))
    out.alpha_composite(plate, (0, int(H * 0.35)))
    return out

if dst.endswith(".png"):
    im = Image.open(src).convert("RGBA"); W, H = im.size
    im.alpha_composite(make_tile(W, H, heavy=False)); m = text_img(int(H * 0.09), 120)
    im.alpha_composite(m, (int(W * 0.6), int(H * 0.22))); im.convert("RGB").save(dst)
else:
    make_tile(1920, 1080, heavy=False).save(tile); text_img(96, 120).save(mark)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", str(tile), "-i", str(mark), "-filter_complex",
                    "[0][1]overlay[a];[a][2]overlay=x='(W-w)/2+(W-w)*0.38*sin(t*0.23)':y='(H-h)/2+(H-h)*0.35*sin(t*0.17+1)'",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "copy", "-movflags", "+faststart", dst], check=True)
print("WROTE", dst)
