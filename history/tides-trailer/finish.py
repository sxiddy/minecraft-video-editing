"""Finishing pass (FINAL_PLAN.md sections 7 and 11).

python finish.py FOOTAGE OVERLAY SOUND MASTER_OUT [WATERMARKED_OUT]
  master:      bloom (screen 10 %), fine temporal grain, vignette; H.264 High CRF 14, AAC 320k
  watermarked: master + tiled "MediaSynx" (7 %) + one drifting mark (18 %)
"""
import pathlib, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
INTER = ROOT / "work_audio" / "Inter.ttf"

def font(size, bold):
    for f in (["C:/Windows/Fonts/segoeuib.ttf"] if bold else ["C:/Windows/Fonts/segoeui.ttf"]):
        if pathlib.Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def watermark_pngs():
    tile = ROOT / "work_audio" / "wm_tile.png"
    mark = ROOT / "work_audio" / "wm_mark.png"
    big = Image.new("RGBA", (2600, 1800), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    f = font(40, True)
    for row, y in enumerate(range(0, 1800, 240)):
        for x in range(-420 if row % 2 else 0, 2600, 420):
            d.text((x, y), "MediaSynx", font=f, fill=(255, 255, 255, int(255 * 0.07)))
    big = big.rotate(-20, resample=Image.BICUBIC)
    big.crop((340, 360, 340 + 1920, 360 + 1080)).save(tile)
    f2 = font(72, True)
    w = int(f2.getlength("MediaSynx")) + 20
    m = Image.new("RGBA", (w, 100), (0, 0, 0, 0))
    ImageDraw.Draw(m).text((10, 5), "MediaSynx", font=f2, fill=(255, 255, 255, int(255 * 0.18)))
    m.save(mark)
    return tile, mark

def run(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)

def master(footage, overlay, sound, dst):
    """footage + bloom (in RGB, so no colour cast) + text overlay, then grain and vignette over everything."""
    fc = ("[0:v]format=gbrp,split[a][b];[b]gblur=sigma=18[g];[a][g]blend=all_mode=screen:all_opacity=0.10[bl];"
          "[bl][1:v]overlay=0:0:format=gbrp[c];"
          "[c]format=yuv444p,noise=alls=5:allf=t,vignette=angle=PI/5,format=yuv420p[v]")
    run("-i", footage, "-i", overlay, "-i", sound, "-filter_complex", fc, "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "14", "-r", "60",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", dst)

def watermark(src, dst):
    tile, mark = watermark_pngs()
    fc = ("[0:v][1:v]overlay=0:0[t];"
          "[t][2:v]overlay=x='(W-w)/2+560*sin(t/7)':y='(H-h)/2+300*sin(t/11)',format=yuv420p[v]")
    run("-i", src, "-loop", "1", "-i", str(tile), "-loop", "1", "-i", str(mark), "-filter_complex", fc,
        "-map", "[v]", "-map", "0:a?", "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-c:a", "copy", "-movflags", "+faststart", dst)

if __name__ == "__main__":
    # python finish.py FOOTAGE OVERLAY SOUND MASTER_OUT [WATERMARKED_OUT]
    master(*sys.argv[1:5])
    if len(sys.argv) > 5:
        watermark(sys.argv[4], sys.argv[5])
