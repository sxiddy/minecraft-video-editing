"""Footage compositor for the Tides SMP V2 edit (timeline_v2.py), in numpy + OpenCV.

python render_v2.py [--at T1,T2,...]       -> stills to ../analysis/v2/at_T.jpg (quick look)
python render_v2.py [--range A,B]          -> WORK/v2/footage.mp4 (1920x1080 60 fps, no audio)

Per shot: graded source -> speed ramp (time remap, frames averaged across the span each output frame
covers, so fast parts get real motion blur) -> push-in + shake -> overlays (god rays, bubbles, flare,
light leak, rain). Between shots: zoom-blur punch, directional-blur whip, flash to white, water ripple,
light-leak dissolve, crossfade or hard cut. Then the 3D title, letterbox and fades.
Chunks render in parallel processes and are joined losslessly.
"""
import math, os, pathlib, subprocess, sys
from concurrent.futures import ProcessPoolExecutor
import cv2
import numpy as np
from overlay_v2 import overlay
from timeline_v2 import FPS, TOTAL, TRANS, TITLE_WINDOWS, BARS_OPEN, FADE_OUT, shots

ROOT = pathlib.Path(__file__).parent
RAW = ROOT.parent / "raw"
INDEX = (ROOT.parent / "analysis" / "index.txt").read_text().split("\n")
WORK = pathlib.Path("C:/Users/Siddharth D/tides-work/v2") / os.environ.get("TRACK", "chill-wave")
TITLE = pathlib.Path("C:/Users/Siddharth D/tides-work/title3d")
W, H = 1920, 1080
BAR = 96
GRADE = ("curves=all='0/0.035 0.5/0.5 1/0.97',colorbalance=rs=-0.04:gs=0.0:bs=0.05:rh=0.05:gh=0.01:bh=-0.04,"
         "eq=contrast=1.05:saturation=1.08")
EXTRA = {18: "eq=brightness=0.05:gamma=1.25,"}
CLIP_LEN = {1: 13.2, 2: 5.3}
S = shots()

def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)

def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2

# ---------------------------------------------------------------- speed ramps
def speed(ramp, u):
    if ramp == "fs":
        return 0.45 + 1.85 * (1 - smooth(u / 0.42))
    if ramp == "sf":
        return 0.5 + 1.9 * smooth((u - 0.55) / 0.45)
    return {"slow": 0.55, "half": 0.5, "n": 1.0}[ramp]

def src_positions(s):
    """Source frame position (float, in source frames) for every output frame of the shot's render window."""
    n = round((s["rb"] - s["ra"]) * FPS)
    v = np.array([speed(s["ramp"], k / max(n - 1, 1)) for k in range(n)])
    pos = np.concatenate([[0.0], np.cumsum(v)[:-1]])
    length = CLIP_LEN.get(s["clip"], 10.0)
    start = s["src"] * FPS
    over = start + pos[-1] + 2 - (length - 0.05) * FPS
    if over > 0:  # never run past the end of the clip: slide the in point back
        start = max(0.8 * FPS, start - over)
        if start + pos[-1] + 2 > (length - 0.05) * FPS:
            pos *= ((length - 0.05) * FPS - 2 - start) / pos[-1]
            v = np.gradient(pos)
    return start + pos, v

for s in S:
    s["pos"], s["vel"] = src_positions(s)

# ---------------------------------------------------------------- source reader
class Reader:
    """Sequential graded RGB frames from one clip, starting at an absolute source frame; small sliding cache."""
    def __init__(self, clip, first):
        self.first = int(first)
        f = RAW / INDEX[clip - 1]
        vf = EXTRA.get(clip, "") + GRADE + ",format=rgb24"
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{self.first / FPS:.4f}", "-i", str(f), "-an",
                                   "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=W * H * 3 * 2)
        self.cache, self.next = {}, self.first
        self.last = None

    def get(self, i):
        i = max(int(i), self.first)
        while self.next <= i:
            buf = self.p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:  # clip ended: hold the last frame
                self.cache[self.next] = self.last
            else:
                self.last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
                self.cache[self.next] = self.last
            self.next += 1
        for k in [k for k in self.cache if k < i - 4]:
            del self.cache[k]
        return self.cache.get(i, self.last)

    def close(self):
        self.p.kill()

def remapped(reader, s, k):
    """Frame k of shot s after the time remap, with frame blending as motion blur."""
    p, v = s["pos"][k], s["vel"][k]
    if v > 1.05:  # fast: average the source frames this output frame sweeps over (75 % shutter)
        a, b = p - 0.375 * v, p + 0.375 * v
        idx = range(int(math.floor(a)), int(math.floor(b)) + 1)
        acc = np.zeros((H, W, 3), np.float32)
        for i in idx:
            acc += reader.get(i)
        return acc / (len(idx) * 255.0)
    f = p - math.floor(p)
    w = smooth((f - 0.25) / 0.5)  # mostly-held frames with a short blend: crisp slow motion, no stutter
    a = reader.get(math.floor(p)).astype(np.float32)
    if w <= 0.001:
        return a / 255.0
    return (a * (1 - w) + reader.get(math.floor(p) + 1).astype(np.float32) * w) / 255.0

# ---------------------------------------------------------------- overlays
LW, LH = 480, 270
ly, lx = np.mgrid[0:LH, 0:LW].astype(np.float32)

def screen(img, layer, strength):
    return 1 - (1 - img) * (1 - np.clip(layer * strength, 0, 1))

def up(layer):
    return cv2.resize(layer, (W, H), interpolation=cv2.INTER_LINEAR)

def god_rays(t, seed):
    cx, cy = LW * (0.45 + 0.1 * math.sin(seed)), -LH * 0.35
    th = np.arctan2(ly - cy, lx - cx)
    r = np.hypot(lx - cx, ly - cy)
    rays = (np.sin(th * 23 + t * 0.6 + seed) * 0.5 + 0.5) * (np.sin(th * 41 - t * 0.9 + seed * 2) * 0.5 + 0.5)
    rays = np.clip(rays * 1.6 - 0.35, 0, 1) * np.exp(-r / (LH * 1.25))
    rays = cv2.GaussianBlur(rays, (0, 0), 2.5)
    return up(np.dstack([rays * 0.70, rays * 0.95, rays * 1.0]))

def bubbles(img, t, seed, k_local):
    rng = np.random.default_rng(seed)
    n = 26
    x0, sp, r, ph = rng.uniform(0, W, n), rng.uniform(70, 220, n), rng.uniform(3, 11, n), rng.uniform(0, 1, n)
    layer = np.zeros((H, W), np.float32)
    for i in range(n):
        y = H + 40 - ((ph[i] * (H + 80) + sp[i] * t) % (H + 80))
        x = x0[i] + 14 * math.sin(t * 2.1 + i)
        cv2.circle(layer, (int(x), int(y)), int(r[i]), 0.55, 2, cv2.LINE_AA)
        cv2.circle(layer, (int(x - r[i] * 0.35), int(y - r[i] * 0.35)), max(1, int(r[i] * 0.25)), 0.9, -1, cv2.LINE_AA)
    layer = cv2.GaussianBlur(layer, (0, 0), 0.8)
    return screen(img, np.dstack([layer * 0.8, layer * 0.95, layer]), 0.6)

def flare(t, seed):
    sx, sy = LW * (0.18 + 0.03 * math.sin(t * 0.4 + seed)), LH * 0.14
    d2 = (lx - sx) ** 2 + (ly - sy) ** 2
    glow = np.exp(-d2 / (2 * (LH * 0.22) ** 2)) * 0.9 + np.exp(-d2 / (2 * (LH * 0.05) ** 2))
    streak = np.exp(-((ly - sy) ** 2) / (2 * 2.2 ** 2)) * np.exp(-np.abs(lx - sx) / (LW * 0.45))
    out = np.dstack([glow * 1.0, glow * 0.78, glow * 0.5]) + np.dstack([streak * 0.55, streak * 0.75, streak * 1.0])
    cx, cy = LW / 2, LH / 2
    for f, rad, col in [(0.6, 9, (0.4, 0.8, 1.0)), (1.25, 16, (1.0, 0.6, 0.3)), (1.6, 6, (0.6, 1.0, 0.7)), (2.0, 24, (0.5, 0.5, 1.0))]:
        gx, gy = sx + (cx - sx) * f, sy + (cy - sy) * f
        g = np.clip(1 - np.sqrt((lx - gx) ** 2 + (ly - gy) ** 2) / rad, 0, 1) ** 1.5 * 0.22
        out += np.dstack([g * col[0], g * col[1], g * col[2]])
    flick = 0.85 + 0.15 * math.sin(t * 3.3 + seed) * math.sin(t * 1.7)
    return up(out.astype(np.float32) * flick)

def leak(t, seed, amt=1.0):
    out = np.zeros((LH, LW, 3), np.float32)
    for j, (col, sz) in enumerate([((1.0, 0.55, 0.2), 0.55), ((1.0, 0.3, 0.35), 0.4), ((1.0, 0.8, 0.45), 0.3)]):
        px = LW * (0.5 + 0.55 * math.sin(t * (0.35 + 0.13 * j) + seed + j * 2.1))
        py = LH * (0.5 + 0.45 * math.cos(t * (0.27 + 0.11 * j) + seed * 1.3 + j))
        g = np.exp(-((lx - px) ** 2 + (ly - py) ** 2) / (2 * (LW * sz) ** 2))
        out += np.dstack([g * col[0], g * col[1], g * col[2]])
    return up(out * amt)

RAIN = None
def rain(img, t, seed):
    rng = np.random.default_rng(seed + 99)
    n = 260
    x0, y0, sp, ln = rng.uniform(0, 960, n), rng.uniform(0, 540, n), rng.uniform(900, 1500, n), rng.uniform(14, 34, n)
    layer = np.zeros((540, 960), np.float32)
    for i in range(n):
        y = (y0[i] + sp[i] * t) % 600 - 30
        x = (x0[i] - 0.18 * sp[i] * t) % 1000 - 20
        cv2.line(layer, (int(x), int(y)), (int(x + ln[i] * 0.18), int(y + ln[i])), 0.5 + 0.5 * (i % 3) / 2, 1, cv2.LINE_AA)
    layer = up(cv2.GaussianBlur(layer, (0, 0), 0.7))
    return screen(img, np.dstack([layer * 0.85, layer * 0.92, layer]), 0.28)

# ---------------------------------------------------------------- per-shot frame
def warp(img, scale, dx, dy):
    m = np.float32([[scale, 0, (1 - scale) * W / 2 + dx], [0, scale, (1 - scale) * H / 2 + dy]])
    return cv2.warpAffine(img, m, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def zoom_blur(img, scale, spread, n=6):
    acc = np.zeros_like(img)
    for j in range(n):
        acc += warp(img, scale * (1 + spread * j / (n - 1)), 0, 0)
    return acc / n

def shot_frame(s, reader, t):
    if "black" in s["ov"]:
        return np.zeros((H, W, 3), np.float32)
    k = min(max(round((t - s["ra"]) * FPS), 0), len(s["pos"]) - 1)
    img = remapped(reader, s, k)
    if "dim" in s["ov"]:  # V3 cold open: footage under the kinetic words
        img = img * 0.42
    u = (t - s["ra"]) / max(s["rb"] - s["ra"], 1e-3)
    scale = 1.0 + 0.07 * u
    for ov in s["ov"]:  # "z1.35" = punch-in reframe (makes cuts between similar wides read, player bigger)
        if ov.startswith("z"):
            scale *= float(ov[1:])
    dx = dy = 0.0
    if s["shake"] and 0 <= t - s["a"] < 0.6:  # impact shake, decaying
        e = math.exp(-(t - s["a"]) * 7) * 14
        dx = e * math.sin((t - s["a"]) * 83)
        dy = e * math.sin((t - s["a"]) * 61 + 1)
        scale += 0.012
    spread = 0.0
    # zoom punch: outgoing pushes in hard, incoming starts pushed in and settles
    if s["tr_out"] == "zoom" and t > s["b"] - TRANS["zoom"][0] / FPS:
        p = (t - (s["b"] - TRANS["zoom"][0] / FPS)) / (TRANS["zoom"][0] / FPS)
        scale *= 1 + 0.45 * p ** 2.2
        spread = 0.10 * p
    if s["tr"] == "zoom" and t < s["a"] + TRANS["zoom"][1] / FPS:
        p = 1 - (t - s["a"] + TRANS["zoom"][1] / FPS) / (2 * TRANS["zoom"][1] / FPS)
        p = max(p, 0)
        scale *= 1 + 0.35 * p ** 1.6
        spread = 0.10 * p
    img = zoom_blur(img, scale, spread) if spread > 0.004 else warp(img, scale, dx, dy)
    if spread > 0.004 and (dx or dy):
        img = warp(img, 1.0, dx, dy)
    tl = t - s["a"]
    seed = s["i"] * 1.7
    for ov in s["ov"]:
        if ov == "rays":
            img = screen(img, god_rays(tl, seed), 0.22)
        elif ov == "bubbles":
            img = bubbles(img, tl, s["i"], k)
        elif ov == "flare":
            img = screen(img, flare(tl, seed), 0.42)
        elif ov == "leak":
            img = screen(img, leak(tl, seed), 0.22)
        elif ov == "rain":
            img = rain(img, tl, s["i"])
            # storm grade: +contrast, teal shadows / warm highlights, bloom
            l = img.mean(2, keepdims=True)
            img = np.clip((img - 0.45) * 1.27 + 0.45 - 0.03, 0, 1)
            img = img + (1 - l) * np.array([-0.045, 0.012, 0.03]) + l * np.array([0.04, 0.015, -0.03])
            bl = cv2.GaussianBlur(cv2.resize(np.clip(img - 0.7, 0, 1).astype(np.float32), (480, 270)), (0, 0), 6)
            img = img + cv2.resize(bl, (W, H)) * 0.8
        elif ov == "bolt":  # lightning: a double flicker 0.05 s and 0.17 s into the shot
            f = max(0.0, 1 - abs(tl - 0.06) / 0.05) + 0.6 * max(0.0, 1 - abs(tl - 0.19) / 0.04)
            img = img + f * 0.55 * np.array([0.85, 0.92, 1.0])
        elif ov == "blur":
            b = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (480, 270), interpolation=cv2.INTER_AREA), (0, 0), 3.2),
                           (W, H), interpolation=cv2.INTER_CUBIC)
            m = smooth((t - s["a"] - 0.1) / 0.6)
            img = img * (1 - m) + b * (0.62 * m)
    return img

# ---------------------------------------------------------------- transitions between shot A (out) and B (in)
GY, GX = np.mgrid[0:H, 0:W].astype(np.float32)
RD = np.hypot(GX - W / 2, GY - H * 0.45) + 1

def transition(kind, A, B, t, cut):
    if kind == "dip":  # P1: impact without white - 4-frame bump to ~70% grey and a 1.02 -> 1.00 push
        u = (t - cut) * FPS
        if u < 0:
            return A
        g = max(0.0, 1 - u / 8) * 0.55
        return B * (1 - g) + 0.7 * g
    ho, hi = TRANS[kind][0] / FPS, TRANS[kind][1] / FPS
    p = (t - (cut - ho)) / (ho + hi)  # 0 -> 1 across the whole transition
    if kind == "fade":
        return A * (1 - smooth(p)) + B * smooth(p)
    if kind == "zoom":  # the per-shot zoom does the punch; swap with a 2-frame mix and a soft flash
        m = smooth((p - 0.44) / 0.12)
        out = A * (1 - m) + B * m
        return screen(out, np.ones_like(out), 0.18 * math.exp(-((p - 0.5) / 0.12) ** 2))
    if kind == "whip":
        o = ease_io(p) * W
        oi = int(round(o))
        out = np.empty_like(A)
        if oi < W:
            out[:, :W - oi] = A[:, oi:]
        if oi > 0:
            out[:, W - oi:] = B[:, :oi]
        vel = W * abs(ease_io(min(p + 0.02, 1)) - ease_io(max(p - 0.02, 0))) / 0.04 / ((ho + hi) * FPS)
        k = int(min(vel * 1.4, 260))
        return cv2.blur(out, (k, 1)) if k > 2 else out
    if kind == "flash":
        if t < cut:
            return screen(A, np.ones_like(A), (p / (ho / (ho + hi))) ** 2)
        q = (t - cut) / hi
        return screen(B, np.ones_like(B), (1 - q) ** 1.8)
    if kind == "ripple":
        amp = 0.02 * W * math.sin(math.pi * p)
        disp = amp * np.sin(RD / W * 60 - p * 14)
        mx = np.clip(GX + disp * (GX - W / 2) / RD, 0, W - 1)
        my = np.clip(GY + disp * (GY - H * 0.45) / RD, 0, H - 1)
        a2 = cv2.remap(A, mx, my, cv2.INTER_LINEAR)
        b2 = cv2.remap(B, mx, my, cv2.INTER_LINEAR)
        m = smooth((p - 0.3) / 0.4)
        out = a2 * (1 - m) + b2 * m
        tint = np.empty_like(out); tint[:] = (0.55, 0.85, 1.0)
        return screen(out, tint, 0.25 * math.sin(math.pi * p))
    if kind == "leak":
        m = smooth((p - 0.2) / 0.6)
        out = A * (1 - m) + B * m
        return screen(out, leak(t, 3.0), 0.75 * math.sin(math.pi * p))
    return B if t >= cut else A

# ---------------------------------------------------------------- title, bars, fades
_title_cache = {}
TITLE_SHADE = np.exp(-(((GX - W / 2) / (W * 0.33)) ** 2 + ((GY - H * 0.47) / (H * 0.36)) ** 2))[..., None]
def title_png(n):
    n = min(max(n, 1), 300)
    if n not in _title_cache:
        f = TITLE / f"{n:04d}.png"
        im = cv2.imread(str(f), cv2.IMREAD_UNCHANGED)
        if im is None:
            return None
        rgba = cv2.cvtColor(im, cv2.COLOR_BGRA2RGBA).astype(np.float32) / 255
        _title_cache.clear()
        _title_cache[n] = rgba
    return _title_cache[n]

def finish_frame(img, t):
    for a, b in TITLE_WINDOWS:  # soft dark backdrop under the 2D pixel logo (drawn by overlay_v2)
        if a <= t < b:
            op = smooth((t - a) / 0.15) * (1 - smooth((t - (b - 0.2)) / 0.2) if b < TOTAL - 0.5 else smooth((t - a) / 0.15))
            img = img * (1 - 0.45 * op * TITLE_SHADE)
    bo = smooth((t - BARS_OPEN[0]) / (BARS_OPEN[1] - BARS_OPEN[0]))
    bar = int(round(BAR * (1 - bo)))
    if bar > 0:
        img[:bar] = 0
        img[H - bar:] = 0
    o = overlay(t)
    if o is not None:
        img = img * (1 - o[..., 3:4]) + o[..., :3] * o[..., 3:4]
    fade = smooth(t / 0.12) * (1 - smooth((t - FADE_OUT[0]) / (FADE_OUT[1] - FADE_OUT[0])))
    return img * fade

# ---------------------------------------------------------------- driver
def frame_at(t, readers):
    act = [s for s in S if s["ra"] <= t < s["rb"]]
    for s in act:
        if s["i"] not in readers:
            k = min(max(round((t - s["ra"]) * FPS), 0), len(s["pos"]) - 1)
            readers[s["i"]] = Reader(s["clip"], max(math.floor(s["pos"][k] - s["vel"][k]) - 1, 0))
    for i in [i for i in readers if i not in {s["i"] for s in act}]:
        readers.pop(i).close()
    frames = {s["i"]: shot_frame(s, readers[s["i"]], t) for s in act}
    if len(act) == 1:
        img = frames[act[0]["i"]]
    else:
        a, b = act[0], act[1]
        img = transition(b["tr"], frames[a["i"]], frames[b["i"]], t, b["a"])
    return finish_frame(np.clip(img, 0, 1), t)

def render_range(args):
    f0, f1, out = args
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "12",
                            "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    readers = {}
    for f in range(f0, f1):
        img = frame_at((f + 0.5) / FPS, readers)
        enc.stdin.write((img * 255 + 0.5).astype(np.uint8).tobytes())
    for r in readers.values():
        r.close()
    enc.stdin.close()
    enc.wait()
    return out

def main():
    WORK.mkdir(parents=True, exist_ok=True)
    args = sys.argv[1:]
    if args and args[0] == "--at":
        for t in [float(x) for x in args[1].split(",")]:
            img = frame_at(t, {})
            cv2.imwrite(str(ROOT.parent / "analysis" / "v2" / f"at_{t:05.2f}.jpg"),
                        cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
        return
    a, b = (0.0, TOTAL)
    if args and args[0] == "--range":
        a, b = [float(x) for x in args[1].split(",")]
    F0, F1 = round(a * FPS), round(b * FPS)
    n = int(os.environ.get("JOBS", "10"))
    step = math.ceil((F1 - F0) / n)
    jobs = [(f, min(f + step, F1), WORK / f"chunk_{j:02d}.mp4") for j, f in enumerate(range(F0, F1, step))]
    with ProcessPoolExecutor(n) as ex:
        parts = list(ex.map(render_range, jobs))
    lst = WORK / "chunks.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    str(WORK / "footage.mp4")], check=True)
    print("WROTE", WORK / "footage.mp4")

if __name__ == "__main__":
    main()
