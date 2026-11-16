"""Text + Minecraft UI layer for the V2 edit, drawn per frame with PIL (pixel fonts, crisp, deterministic).

overlay(t) -> RGBA float32 (H, W, 4) or None.   events() -> [(time, kind)] for UI sounds (clicks, key ticks, pops).
Style follows the client reference (RuneSpire trailer): Minecraft-style pixel type, white->sky gradient headlines
with a dark drop shadow, per-letter decode reveal with glow, recreated in-game UI.
"""
import math, pathlib
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from timeline_v2 import TEXT, INFO, TOTAL

W, H = 1920, 1080
FD = pathlib.Path(__file__).parent / "assets" / "fonts" / "pixel"
PS2P = str(FD / "PressStart2P.ttf")
MONO = str(FD / "ttf" / "Monocraft-ttf" / "Monocraft.ttf")
MONO_B = str(FD / "ttf" / "Monocraft-ttf" / "weights" / "Monocraft-Bold.ttf")
_fonts = {}
def font(path, size, weight=None):
    if (path, size, weight) not in _fonts:
        f = ImageFont.truetype(path, size)
        if weight:
            f.set_variation_by_axes([weight])
        _fonts[(path, size, weight)] = f
    return _fonts[(path, size, weight)]

GLITCH = "#%&@*+=?/<>$"
JAVA = "pm-twirl.gl.joinmc.link"
BEDROCK = "listed-completing.gl.at.ply.gg"
PORT = "35634"

def clamp(x, a=0.0, b=1.0):
    return min(max(x, a), b)

def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def back_out(x, s=1.9):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2

# ---------------------------------------------------------------- text primitives
def gradient(size, top, bot):
    h = size[1]
    g = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(top)[None, None] * (1 - g) + np.array(bot)[None, None] * g).repeat(size[0], 1)
    return Image.fromarray(arr.astype(np.uint8), "RGB")

def draw_text(canvas, xy, text, fnt, fill=(255, 255, 255), grad=None, shadow=4, alpha=1.0, anchor="la"):
    """Minecraft-style text: a darker copy offset down-right, then the face (flat or vertical gradient)."""
    if alpha <= 0 or not text:
        return
    x, y = xy
    l, t, r, b = fnt.getbbox(text, anchor=anchor)
    w, h = r - l + shadow + 2, b - t + shadow + 2
    m = Image.new("L", (w, h))
    ImageDraw.Draw(m).text((-l, -t), text, font=fnt, fill=255, anchor=anchor)
    a = int(255 * alpha)
    if shadow:
        sh = Image.new("RGBA", (w, h), (8, 16, 30, 0))
        sh.putalpha(m.point(lambda v: v * a // 255 * 0.85))
        canvas.alpha_composite(sh, (int(x + l + shadow), int(y + t + shadow)))
    face = (gradient((w, h), *grad) if grad else Image.new("RGB", (w, h), fill)).convert("RGBA")
    face.putalpha(m.point(lambda v: v * a // 255))
    canvas.alpha_composite(face, (int(x + l), int(y + t)))

def decode(text, t, t0, stagger=0.035, settle=0.14, seed=0):
    """Per-letter decode: each letter shows cycling glyphs for `settle` s, then locks. Returns (shown, n_locked)."""
    out, locked = [], 0
    for i, ch in enumerate(text):
        ti = t0 + i * stagger
        if t < ti:
            out.append(" ")
        elif t < ti + settle and ch != " ":
            out.append(GLITCH[(int(t * 30) + i * 7 + seed) % len(GLITCH)])
        else:
            out.append(ch); locked += 1
    return "".join(out), locked

SKY = ((255, 255, 255), (120, 205, 255))
GOLD = ((255, 247, 210), (255, 184, 70))

def glow_layer(img, strength=0.9, sigma=14, tint=(0.55, 0.85, 1.0)):
    """Additive soft glow from the layer's alpha (applied in numpy after drawing)."""
    a = np.asarray(img, np.float32)[..., 3] / 255
    g = cv2.GaussianBlur(a, (0, 0), sigma) * strength
    return np.dstack([g * tint[0], g * tint[1], g * tint[2]])

# ---------------------------------------------------------------- captions
def caption(cv, t, a, b, main, sub=None, y=455, big=44, seed=0):
    """Feature caption: PS2P headline (gradient) + Monocraft subline, decode in, lift-and-fade out."""
    if not (a - 0.05 <= t < b + 0.5):
        return False
    out = smooth((t - b) / 0.45)
    alpha = 1 - out
    dy = -18 * out
    fm = font(PS2P, big)
    shown, _ = decode(main.upper(), t, a, 0.03, 0.12, seed)
    wfull = fm.getlength(main.upper())
    draw_text(cv, (W / 2 - wfull / 2, y + dy), shown, fm, grad=SKY, shadow=5, alpha=alpha)
    if sub:
        fs = font(MONO, 30)
        s_shown, _ = decode(sub, t, a + 0.35, 0.02, 0.1, seed + 3)
        ws = fs.getlength(sub)
        draw_text(cv, (W / 2 - ws / 2, y + big + 30 + dy), s_shown, fs, fill=(225, 238, 245), shadow=3, alpha=alpha * 0.95)
        # thin rule between the lines, drawing out from the centre
        k = smooth((t - a - 0.2) / 0.5) * alpha
        if k > 0:
            ImageDraw.Draw(cv).rectangle([W / 2 - 140 * k, y + big + 14 + dy, W / 2 + 140 * k, y + big + 16 + dy],
                                         fill=(255, 210, 120, int(220 * k)))
    return True

def line(cv, t, a, b, text, y=500, size=36, seed=0):
    if not (a - 0.05 <= t < b + 0.5):
        return False
    alpha = 1 - smooth((t - b) / 0.45)
    f = font(MONO_B, size)
    shown, _ = decode(text, t, a, 0.028, 0.1, seed)
    w = f.getlength(text)
    draw_text(cv, (W / 2 - w / 2, y), shown, f, fill=(240, 246, 250), shadow=3, alpha=alpha)
    return True

# ---------------------------------------------------------------- Minecraft UI
S = 3  # GUI scale

def mc_button(d, x, y, w, label, hover=False, pressed=False, alpha=1.0):
    a = int(255 * alpha)
    d.rectangle([x, y, x + w, y + 20 * S], fill=(0, 0, 0, a))
    face = (60, 60, 60) if pressed else ((126, 136, 191) if hover else (111, 111, 111))
    d.rectangle([x + S, y + S, x + w - S, y + 20 * S - S], fill=(*face, a))
    d.rectangle([x + S, y + S, x + w - S, y + 2 * S], fill=(*[min(255, c + 48) for c in face], a))
    d.rectangle([x + S, y + 17 * S, x + w - S, y + 19 * S], fill=(*[max(0, c - 40) for c in face], a))
    if hover:
        d.rectangle([x, y, x + w, y + 20 * S], outline=(255, 255, 255, a), width=S)

def mc_label(cv, x, y, w, label, alpha=1.0, color=(255, 255, 255)):
    f = font(MONO, 26)
    tw = f.getlength(label)
    draw_text(cv, (x + w / 2 - tw / 2, y + 16), label, f, fill=color, shadow=3, alpha=alpha)

def field(cv, d, x, y, w, text, caret, alpha=1.0, active=False):
    a = int(255 * alpha)
    d.rectangle([x, y, x + w, y + 20 * S], fill=(0, 0, 0, a), outline=((255, 255, 255, a) if active else (160, 160, 160, a)), width=S)
    f = font(MONO, 26)
    draw_text(cv, (x + 14, y + 16), text + ("_" if caret else ""), f, fill=(224, 224, 224), shadow=3, alpha=alpha)

def droplet_icon(cv, x, y, size=96, alpha=1.0):
    """8x8 pixel-art water drop as the server icon."""
    grid = ["...##...", "..#aa#..", ".#aaaa#.", ".#awaa#.", "#aawaaa#", "#aaaaaa#", ".#aaaa#.", "..####.."]
    px = size // 8
    d = ImageDraw.Draw(cv)
    d.rectangle([x, y, x + size, y + size], fill=(20, 52, 84, int(255 * alpha)))
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            col = {"#": (18, 70, 140), "a": (64, 170, 255), "w": (220, 245, 255)}.get(ch)
            if col:
                shade = 1 - r * 0.04
                d.rectangle([x + c * px, y + r * px, x + c * px + px - 1, y + r * px + px - 1],
                            fill=(*[int(v * shade) for v in col], int(255 * alpha)))

def ping_bars(d, x, y, t_on, t, alpha=1.0):
    for i in range(5):
        h = (i + 1) * 2 * S + 2
        lit = t - t_on > 0.08 * i
        col = (0, 230, 60) if lit else (40, 40, 40)
        d.rectangle([x + i * 3 * S, y + 8 * S - h, x + i * 3 * S + 2 * S - 1, y + 8 * S], fill=(*col, int(255 * alpha)))

def server_row(cv, x, y, t, t_on, name, motd, tag, players, alpha=1.0):
    k = back_out((t - t_on) / 0.35)
    if k <= 0:
        return
    rw, rh = 305 * S, 36 * S
    row = Image.new("RGBA", (rw + 20, rh + 20))
    d = ImageDraw.Draw(row)
    d.rectangle([2, 2, rw + 2, rh + 2], fill=(0, 0, 0, 150), outline=(128, 128, 128, 255), width=S)
    droplet_icon(row, 8, 8, 32 * S - 4)
    draw_text(row, (32 * S + 20, 14), name, font(MONO_B, 28), fill=(255, 255, 255), shadow=3)
    draw_text(row, (32 * S + 20, 52), motd[0], font(MONO, 22), fill=(120, 205, 255), shadow=2)
    draw_text(row, (32 * S + 20, 80), motd[1], font(MONO, 22), fill=(170, 170, 170), shadow=2)
    pf = font(MONO, 22)
    draw_text(row, (rw - 60 - pf.getlength(players), 14), players, pf, fill=(170, 170, 170), shadow=2)
    ping_bars(d, rw - 46, 12, t_on + 0.25, t)
    tf = font(PS2P, 14)
    tw = tf.getlength(tag)
    d.rectangle([rw - tw - 30, rh - 34, rw - 8, rh - 8], fill=(255, 184, 70, 255))
    draw_text(row, (rw - tw - 19, rh - 28), tag, tf, fill=(30, 20, 5), shadow=0)
    sc = 0.6 + 0.4 * k
    row = row.resize((max(1, int(row.width * sc)), max(1, int(row.height * sc))), Image.NEAREST)
    a = np.asarray(row).copy()
    a[..., 3] = (a[..., 3] * clamp(alpha * min(1, k * 1.5))).astype(np.uint8)
    cv.alpha_composite(Image.fromarray(a), (int(x + (rw + 20) * (1 - sc) / 2), int(y + (rh + 20) * (1 - sc) / 2)))

def cursor(cv, x, y, down=False):
    return  # review 3: hide the mouse cursor (reads as a screen recording)

    arrow = ["#.........", "##........", "#w#.......", "#ww#......", "#www#.....", "#wwww#....", "#wwwww#...",
             "#wwwwww#..", "#wwww####.", "#w##w#....", "##..#w#...", ".....#w#..", "......##.."]
    px = 4 if not down else 3
    d = ImageDraw.Draw(cv)
    for r, row in enumerate(arrow):
        for c, ch in enumerate(row):
            if ch != ".":
                col = (0, 0, 0, 255) if ch == "#" else (255, 255, 255, 255)
                d.rectangle([x + c * px, y + r * px, x + c * px + px - 1, y + r * px + px - 1], fill=col)

def typed(text, t, t0, cps=22):
    n = int(clamp((t - t0) * cps, 0, len(text)))
    return text[:n]

# Info section script, in seconds from INFO[0]
I0, I1 = INFO
INFO_REF = 8.6
def info_screen(cv, t):
    """Drawn on a 1440x810 canvas and scaled up 4/3, so the UI reads at trailer size (GUI scale 4 on 1080p)."""
    global I1
    if not (I0 <= t < I1 + 0.5):
        return False
    global W, H
    W, H = 1440, 810
    small = Image.new("RGBA", (W, H))
    k = INFO_REF / (INFO[1] - INFO[0])  # the UI choreography was timed for INFO_REF s; play it compressed
    real = I1
    I1 = I0 + INFO_REF
    try:
        _info(small, I0 + (min(t, real + 0.5) - I0) * k if t < real else I1 + (t - real))
    finally:
        I1 = real
        W, H = 1920, 1080
    cv.alpha_composite(small.resize((1920, 1080), Image.LANCZOS))
    return True

def _info(cv, t):
    LIST_X, LIST_Y = W / 2 - 305 * S / 2 - 10, 150
    BTN_Y = H - 190
    u = t - I0
    alpha = smooth(u / 0.4) * (1 - smooth((t - I1) / 0.45))
    d = ImageDraw.Draw(cv)
    # header + darkened list area like the real menu
    d.rectangle([0, 120, W, BTN_Y - 30], fill=(0, 0, 0, int(110 * alpha)))
    d.rectangle([0, 118, W, 121], fill=(0, 0, 0, int(200 * alpha)))
    d.rectangle([0, BTN_Y - 32, W, BTN_Y - 29], fill=(0, 0, 0, int(200 * alpha)))
    hf = font(MONO_B, 34)
    hdr = "Play Multiplayer"
    edit = 1.1 <= u < 3.55       # Java: Edit Server Info screen
    bed = 4.85 <= u < 6.9        # Bedrock: Add External Server screen
    if edit or bed:
        hdr = "Edit Server Info" if edit else "Add External Server"
    draw_text(cv, (W / 2 - hf.getlength(hdr) / 2, 62), hdr, hf, fill=(255, 255, 255), shadow=3, alpha=alpha)
    bw = 200 * S // 2 - 6
    if edit:
        v = u - 1.1
        draw_text(cv, (W / 2 - 300, 300), "Server Name", font(MONO, 24), fill=(160, 160, 160), shadow=2, alpha=alpha)
        field(cv, d, W / 2 - 300, 336, 600, typed("Tides SMP", u, 1.3, 16), int(u * 4) % 2 == 0 and v < 0.9, alpha, v < 0.9)
        draw_text(cv, (W / 2 - 300, 440), "Server Address", font(MONO, 24), fill=(160, 160, 160), shadow=2, alpha=alpha)
        field(cv, d, W / 2 - 300, 476, 600, typed(JAVA, u, 2.0, 24), int(u * 4) % 2 == 0 and v >= 0.9, alpha, v >= 0.9)
        hov = u > 3.1
        mc_button(d, W / 2 - 300, 640, 600, "Done", hover=hov, pressed=3.35 < u < 3.45, alpha=alpha)
        mc_label(cv, W / 2 - 300, 640, 600, "Done", alpha)
        cx, cy = (W / 2 + 120 + (1 - smooth((u - 2.9) / 0.3)) * 260, 660 + (1 - smooth((u - 2.9) / 0.3)) * 120)
        cursor(cv, int(cx), int(cy), 3.35 < u < 3.45)
        return True
    if bed:
        v = u - 4.85
        for i, (lab, val, t0, cps) in enumerate([("Server Name", "Tides SMP", 4.95, 18), ("Server Address", BEDROCK, 5.35, 30),
                                                  ("Port", PORT, 6.25, 14)]):
            yy = 270 + i * 130
            draw_text(cv, (W / 2 - 300, yy), lab, font(MONO, 24), fill=(160, 160, 160), shadow=2, alpha=alpha)
            field(cv, d, W / 2 - 300, yy + 36, 600 if i < 2 else 220, typed(val, u, t0, cps), False, alpha,
                  t0 <= u < t0 + len(val) / cps + 0.2)
        mc_button(d, W / 2 - 300, 690, 600, "Save", hover=u > 6.55, pressed=6.7 < u < 6.8, alpha=alpha)
        mc_label(cv, W / 2 - 300, 690, 600, "Save", alpha)
        cursor(cv, int(W / 2 + 100 + (1 - smooth((u - 6.3) / 0.3)) * 240), int(705 + (1 - smooth((u - 6.3) / 0.3)) * 60),
               6.7 < u < 6.8)
        return True
    # server list
    server_row(cv, LIST_X, LIST_Y, t, I0 + 3.6, "Tides SMP", ("A calm water-world survival server", JAVA), "JAVA",
               "128/500", alpha)
    server_row(cv, LIST_X, LIST_Y + 36 * S + 24, t, I0 + 7.0, "Tides SMP",
               ("Bedrock  " + BEDROCK, "Port " + PORT), "BEDROCK", "128/500", alpha)
    labels = [["Join Server", "Direct Connection", "Add Server"], ["Edit", "Delete", "Refresh", "Cancel"]]
    for r, row in enumerate(labels):
        n = len(row)
        bw = (930 - (n - 1) * 12) / n
        for c, lab in enumerate(row):
            x = W / 2 - 465 + c * (bw + 12)
            y = BTN_Y + r * (20 * S + 12)
            hov = lab == "Add Server" and (0.55 < u < 1.1 or 4.2 < u < 4.85)
            prs = lab == "Add Server" and (0.95 < u < 1.05 or 4.7 < u < 4.8)
            mc_button(d, x, y, bw, lab, hover=hov, pressed=prs, alpha=alpha)
            mc_label(cv, x, y, bw, lab, alpha)
    # cursor heads to Add Server twice
    ax, ay = W / 2 - 465 + 2 * (310 + 4) + 150, BTN_Y + 30
    if u < 1.1:
        k = smooth((u - 0.2) / 0.5)
        cursor(cv, int(W / 2 + 260 + (ax - W / 2 - 260) * k), int(560 + (ay - 560) * k), 0.95 < u < 1.05)
    elif 3.55 <= u < 4.85:
        k = smooth((u - 3.9) / 0.4)
        cursor(cv, int(W / 2 + 120 + (ax - W / 2 - 120) * k), int(660 + (ay - 660) * k), 4.7 < u < 4.8)
    # the droplet note (removed in review 4: read as garbled UI)
    if False:
        k = smooth((u - 7.6) / 0.4)
        nt = ".Steve"
        f = font(MONO_B, 40)
        tw = f.getlength(nt)
        x0, y0 = W / 2 - tw / 2, 440
        d.rectangle([x0 - 16, y0 - 12, x0 + tw + 16, y0 + 56], fill=(0, 0, 0, int(140 * k * alpha)))
        drop = smooth((u - 7.6) / 0.45)
        draw_text(cv, (x0 + f.getlength("."), y0), "Steve", f, fill=(255, 255, 255), shadow=3, alpha=k * alpha)
        if drop < 1:  # the drop falls into place as the leading "."
            yy = y0 - 260 * (1 - drop) ** 2
            d.ellipse([x0 + 2, yy + 18, x0 + 18, yy + 40], fill=(120, 210, 255, int(255 * alpha)))
        else:
            draw_text(cv, (x0, y0), ".", f, fill=(120, 210, 255), shadow=3, alpha=alpha)
            r = (u - 8.05) * 150
            if r < 90:
                d.ellipse([x0 + 10 - r, y0 + 34 - r * 0.35, x0 + 10 + r, y0 + 34 + r * 0.35],
                          outline=(160, 225, 255, int(200 * (1 - r / 90) * alpha)), width=3)
        note = "Bedrock players: your name starts with a dot"
        line(cv, t, I0 + 7.9, I1, note, y=520, size=28, seed=9)
    return True

# ---------------------------------------------------------------- frame
# ---------------------------------------------------------------- pixel type (STYLE GUIDE v3)
import pixel_text as PT
_pt = {}
def ptext(text, style, px, fnt=None):
    k = (text, style, px, fnt)
    if k not in _pt:
        arr = PT.render(text, style, px, font=fnt)
        fam = fnt or PT.STYLES[style]["font"]
        spans = [((PT.PAD + x0) * px, (PT.PAD + x1) * px) for x0, x1 in PT.glyph_spans(text, fam)]
        _pt[k] = (arr, spans)
    return _pt[k]

def ptype(cv, t, a, b, text, style, px, y, fnt=None, x=None, seed=0, dur=0.22, out=0.12, cut_out=False, alpha=1.0):
    """Pixel text with a random-order per-letter decode in (each letter pops white for 2 frames), hold, then a
    short fade (or a hard cut on the beat). y = top of the text box; x None = centred."""
    if not (a <= t < b + out):
        return False
    arr, spans = ptext(text, style, px, fnt)
    h, w = arr.shape[:2]
    x0 = int((W - w) / 2) if x is None else int(x)
    op = alpha * (0.0 if (cut_out and t >= b) else 1 - smooth((t - b) / out))
    if op <= 0:
        return False
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(spans))
    vis = np.zeros(w, np.float32)
    white = np.zeros(w, bool)
    for i, (s0, s1) in enumerate(spans):
        ti = a + dur * order[i] / max(1, len(spans) - 1)
        if t >= ti:
            vis[s0:s1 + px] = 1
            if t < ti + 2 / 60:
                white[s0:s1 + px] = True
    vis[:spans[0][0]] = vis[spans[0][0]] if spans else 1
    vis[spans[-1][1]:] = 1 if t >= a + dur else 0
    im = arr.astype(np.float32).copy()
    im[:, white, :3] = 255
    im[..., 3] *= vis[None, :] * op
    cv.alpha_composite(Image.fromarray(im.clip(0, 255).astype(np.uint8)), (x0, int(y)))
    return True

SANS_B = str(pathlib.Path(__file__).parent / "assets" / "fonts" / "opt" / "LilitaOne-Regular.ttf")  # client pick (option 5)
SANS_M = str(pathlib.Path(__file__).parent / "assets" / "fonts" / "sans" / "Montserrat-SemiBold.ttf")

def stext(cv, t, a, b, text, path, size, y, track=0.18, seed=0, dur=0.3, fade=0.1, out=0.15, cut_out=False,
          alpha=1.0, fill=(255, 255, 255), outline=0):
    """Clean trailer caption over footage (research: caps sans, wide tracking, soft shadow only). Letters fade
    in from blur in random order over `dur`, lift 6 px while settling; out on a hard cut or a short fade."""
    if not (a <= t < b + out):
        return False
    op = alpha * (0.0 if (cut_out and t >= b) else 1 - smooth((t - b) / out))
    if op <= 0:
        return False
    f = font(path, size)
    adv = [f.getlength(c) + size * track for c in text]
    tw = sum(adv) - size * track
    x = (W - tw) / 2
    asc, desc = f.getmetrics()
    lay = Image.new("L", (W, asc + desc + 40))
    d = ImageDraw.Draw(lay)
    order = np.random.default_rng(seed).permutation(len(text))
    for i, c in enumerate(text):
        k = smooth((t - a - dur * order[i] / max(1, len(text) - 1)) / fade)
        if k > 0 and c != " ":
            d.text((x, 20 + 6 * (1 - k)), c, font=f, fill=int(255 * k))
        x += adv[i]
    m = np.asarray(lay, np.float32) / 255 * op
    if outline:  # chunky navy outline under the face (Lilita style)
        ol = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * outline + 1, 2 * outline + 1)))
        stext_outline = ol
    sh = cv2.GaussianBlur(m if not outline else ol, (0, 0), size * 0.12) * 0.6
    y0 = int(y) - 20
    base = np.asarray(cv, np.float32).copy()
    h = m.shape[0]
    y1 = min(H, y0 + h)
    reg = base[y0 + 3:y1 + 3 if y1 + 3 <= H else H]
    shv = sh[:reg.shape[0]]
    reg[..., 3] = np.maximum(reg[..., 3], shv * 255)
    reg[..., :3] *= (1 - shv[..., None])
    reg2 = base[y0:y1]
    if outline:
        ov_ = ol[:y1 - y0, :, None]
        a2 = reg2[..., 3:4] / 255
        oa = ov_ + a2 * (1 - ov_)
        reg2[..., :3] = (np.array([18, 46, 88]) * ov_ + reg2[..., :3] * a2 * (1 - ov_)) / np.maximum(oa, 1e-4)
        reg2[..., 3:4] = oa * 255
    mv = m[:y1 - y0, :, None]
    a2 = reg2[..., 3:4] / 255
    out_a = mv + a2 * (1 - mv)
    reg2[..., :3] = (np.array(fill) * mv + reg2[..., :3] * a2 * (1 - mv)) / np.maximum(out_a, 1e-4)
    reg2[..., 3:4] = out_a * 255
    cv.paste(Image.fromarray(base.clip(0, 255).astype(np.uint8)))
    return True

def sparkles(cv, t, a, cx, cy, w, h, seed=0):
    """Minecraft-style 4-point sparkles twinkling around a pop-up."""
    d = ImageDraw.Draw(cv)
    rng = np.random.default_rng(seed)
    for k in range(14):
        sx, sy = cx + rng.uniform(-w * 0.6, w * 0.6), cy + rng.uniform(-h, h)
        ph = rng.uniform(0, 1.2)
        u = ((t - a - ph * 0.3) * 1.6) % 1.2
        if t < a + ph * 0.3 or u > 1:
            continue
        r = 10 * math.sin(math.pi * u)
        c = (255, 240, 170, int(230 * math.sin(math.pi * u)))
        d.rectangle([sx - r, sy - 2, sx + r, sy + 2], fill=c)
        d.rectangle([sx - 2, sy - r, sx + 2, sy + r], fill=c)

def toast(cv, t, a, b, title, sub):
    """Advancement toast sliding in top-right, the way the game shows it."""
    if not (a <= t < b + 0.4):
        return False
    k = smooth((t - a) / 0.25) * (1 - smooth((t - b) / 0.35))
    bw, bh = 720, 150
    x = W - 40 - bw * k
    y = 124
    d = ImageDraw.Draw(cv)
    d.rectangle([x, y, x + bw, y + bh], fill=(33, 33, 33, 235), outline=(85, 85, 85, 255), width=4)
    d.rectangle([x + 4, y + 4, x + bw - 4, y + 8], fill=(60, 60, 60, 255))
    droplet_icon(cv, int(x + 22), int(y + 22), 104)
    t_arr, _ = ptext(title, "gold", 5)
    s_arr, _ = ptext(sub, "white", 5)
    cv.alpha_composite(Image.fromarray(t_arr), (int(x + 140), y + 10))
    cv.alpha_composite(Image.fromarray(s_arr), (int(x + 140), y + 74))
    return True

_logo_cache = {}
def logo_img(size=190):
    """Premium chunky server logo (client: pixel type over footage looked odd): Lilita One, white->sky->ocean
    vertical gradient, thick navy outline, thin gold rim, soft drop shadow and cyan glow."""
    if size in _logo_cache:
        return _logo_cache[size]
    f = font(SANS_B, size)
    txt, track = "TIDES SMP", 0.02
    adv = [f.getlength(c) + size * track for c in txt]
    tw = int(sum(adv)); pad = int(size * 0.45)
    Wl, Hl = tw + 2 * pad, int(size * 1.25) + 2 * pad
    m = Image.new("L", (Wl, Hl)); d = ImageDraw.Draw(m); x = pad
    for c, a_ in zip(txt, adv):
        d.text((x, pad), c, font=f, fill=255); x += a_
    M = np.asarray(m, np.float32) / 255
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    navy = cv2.dilate(M, k(int(size * 0.07)))
    gold = cv2.dilate(M, k(int(size * 0.095)))
    ys = np.where(M.max(1) > 0.5)[0]; y0, y1 = ys[0], ys[-1]
    g = np.clip((np.arange(Hl) - y0) / max(1, y1 - y0), 0, 1)[:, None]
    stops = np.array([[255, 255, 255], [196, 240, 255], [92, 196, 250], [28, 118, 214]], np.float32)
    seg = np.clip(g * 3, 0, 2.999); i = seg.astype(int); fr = seg - i
    face = stops[i[:, 0]] * (1 - fr) + stops[np.minimum(i[:, 0] + 1, 3)] * fr
    face = np.repeat(face[:, None, :], Wl, 1)
    hl = (np.abs(np.arange(Hl) - (y0 + (y1 - y0) * 0.47)) < size * 0.025)[:, None, None]  # glossy split line
    face = np.where(hl, face * 0.9, face)
    out = np.zeros((Hl, Wl, 4), np.float32)
    sh = cv2.GaussianBlur(np.roll(np.roll(gold, int(size * 0.06), 0), int(size * 0.03), 1), (0, 0), size * 0.05)
    glow = cv2.GaussianBlur(gold, (0, 0), size * 0.18)
    def over(rgb, a):
        a = a[..., None]
        out[..., :3] = rgb * a + out[..., :3] * out[..., 3:4] * (1 - a)
        out[..., 3:4] = a + out[..., 3:4] * (1 - a)
        out[..., :3] /= np.maximum(out[..., 3:4], 1e-4)
    over(np.array([90, 200, 255], np.float32), glow * 0.45)
    over(np.zeros(3, np.float32), sh * 0.7)
    over(np.array([240, 184, 80], np.float32), gold)
    over(np.array([14, 36, 78], np.float32), navy)
    over(face, M)
    out[..., 3] *= 255
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    _logo_cache[size] = img
    return img

# ---------------------------------------------------------------- cinematic type (client: general title-design research)
CF = pathlib.Path(__file__).parent / "assets" / "fonts" / "cine"
CINZEL, MANROPE = str(CF / "Cinzel.ttf"), str(CF / "Manrope.ttf")

def cine(cv, t, a, b, text, path, size, y, weight=None, track=0.12, dur=0.35, rise=10, blur=14, out=0.25,
         fill=(255, 255, 255), glow=0.0, seed=0, alpha=1.0, order="lr", sweep=None, ripple=0.0, cut_out=False,
         fade=0.3, ease=None):
    """Film-title text: letters resolve from blur (staggered), settle upward, optional light sweep and water
    ripple on the reveal, soft shadow + warm glow. Out: blur-fade (or a hard cut on the beat)."""
    if not (a <= t < b + out):
        return False
    op = alpha * (0.0 if (cut_out and t >= b) else 1 - smooth((t - b) / out))
    if op <= 0:
        return False
    f = font(path, size, weight)
    adv = [f.getlength(c) + size * track for c in text]
    tw = sum(adv) - size * track
    asc, desc = f.getmetrics()
    hh = asc + desc + 2 * blur + 20
    lay = np.zeros((hh, W), np.float32)
    n = len(text)
    if order == "lr":
        idx = np.arange(n, dtype=float)
    elif order == "mid":
        idx = np.abs(np.arange(n) - (n - 1) / 2)
    else:
        idx = np.random.default_rng(seed).permutation(n).astype(float)
    idx = idx / max(1.0, idx.max())
    x = (W - tw) / 2
    for i, c in enumerate(text):
        k = (ease or smooth)((t - a - dur * idx[i]) / fade)
        if k > 0 and c != " ":
            g = Image.new("L", (int(adv[i] + 4 * blur), hh))
            ImageDraw.Draw(g).text((2 * blur, blur + 10 + rise * (1 - k)), c, font=f, fill=255)
            gm = np.asarray(g, np.float32) / 255
            if k < 0.999:
                gm = cv2.GaussianBlur(gm, (0, 0), 0.1 + blur * (1 - k)) * k
            x0 = int(x - 2 * blur)
            xa, xb = max(0, x0), min(W, x0 + gm.shape[1])
            if xb > xa:
                lay[:, xa:xb] = np.maximum(lay[:, xa:xb], gm[:, xa - x0:xb - x0])
        x += adv[i]
    if ripple > 0:  # water ripple on the reveal: rows shift sideways, decaying
        rk = ripple * (1 - smooth((t - a) / 0.9))
        if rk > 0.01:
            yy = np.arange(hh, dtype=np.float32)
            mx = (np.arange(W, dtype=np.float32)[None, :] + rk * 18 * np.sin(yy[:, None] * 0.09 + t * 14)).astype(np.float32)
            my = np.repeat(yy[:, None], W, 1).astype(np.float32)
            lay = cv2.remap(lay, mx, my, cv2.INTER_LINEAR)
    lay *= op
    face = np.zeros((hh, W, 3), np.float32) + np.array(fill, np.float32)
    if sweep is not None:  # light sweep: a soft bright diagonal band passing left -> right
        u = (t - a - sweep) / 0.9
        if 0 < u < 1:
            xx = np.arange(W)[None, :] - (np.arange(hh)[:, None] * 0.35)
            band = np.exp(-((xx - (-200 + u * (W + 400))) / 90.0) ** 2)
            face = face + band[..., None] * 120
    y0 = int(y) - blur - 10
    base = np.asarray(cv, np.float32).copy()
    ya, yb = max(0, y0), min(H, y0 + hh)
    L = lay[ya - y0:yb - y0]
    Fc = np.clip(face[ya - y0:yb - y0], 0, 255)
    reg = base[ya:yb]

    def comp(rgb, a1):
        a1 = np.clip(a1, 0, 1)[..., None]
        a0 = reg[..., 3:4] / 255
        oa = a1 + a0 * (1 - a1)
        reg[..., :3] = (rgb * a1 + reg[..., :3] * a0 * (1 - a1)) / np.maximum(oa, 1e-4)
        reg[..., 3:4] = oa * 255

    comp(np.zeros(3, np.float32), cv2.GaussianBlur(L, (0, 0), size * 0.08) * 0.55)
    if glow:
        comp(np.array([255, 236, 200], np.float32), cv2.GaussianBlur(L, (0, 0), size * 0.3) * glow)
    comp(Fc, L)
    cv.paste(Image.fromarray(base.clip(0, 255).astype(np.uint8)))
    return True

def expo_out(x):
    x = clamp(x)
    return 1 - 2 ** (-10 * x) if x < 1 else 1.0

def kinetic(cv, t):
    """Cold open on the beat: each line's letters rise from 8% FH below, blur 12 -> 0, 2-frame stagger, expo-out
    over 14 frames; lines grow 5% -> 6% -> 7.5% FH; JUST THE TIDE in Cinzel 9% FH with tracking collapsing.
    Each line wipes out over 6 frames into the next."""
    from timeline_v2 import KINETIC, B
    spec = [(MANROPE, 54, 800, 0.04), (MANROPE, 65, 800, 0.04), (MANROPE, 81, 800, 0.04), (CINZEL, 97, 900, None)]
    drew = False
    for i, (tw_, word) in enumerate(KINETIC):
        t_end = KINETIC[i + 1][0] if i + 1 < len(KINETIC) else B(0)
        if not (tw_ <= t < t_end):
            continue
        path, size, wt, tr = spec[i]
        if tr is None:  # tracking +300 -> +120 (em/1000) over the hold
            tr = 0.12 + 0.18 * (1 - expo_out((t - tw_) / 0.6))
        col = (255, 255, 255) if i < len(KINETIC) - 1 else (243, 225, 180)
        wipe = clamp((t - (t_end - 0.1)) / 0.1)  # 6-frame exit
        drew |= cine(cv, t, tw_, t_end + 0.2, word, path, size, H / 2 - size * 0.6 - 30 * wipe, weight=wt,
                     track=tr, dur=len(word) * 2 / 60, rise=int(0.08 * H), blur=12, fade=14 / 60, ease=expo_out,
                     fill=col, glow=0.25 if i == len(KINETIC) - 1 else 0.0, alpha=1 - wipe, order="lr")
    return drew

def title_card(cv, t, a, b, y=360, size=230, kicker=True, sub=True):
    """TIDES: wide-tracked Cinzel Black resolving out of a water ripple, a light sweep across it,
    kicker above and a gold rule + tracked subline below (film-title layout)."""
    if not (a <= t < b + 0.4):
        return False
    if kicker:
        cine(cv, t, a + 0.15, b, "A  SURVIVAL  SMP", MANROPE, 28, y - 50, weight=600, track=0.25, dur=0.4,
             blur=6, rise=4, fill=(235, 242, 248), order="mid", seed=1)
    e = expo_out((t - a) / 0.4)  # tracking +600 -> +140, blur 20 -> 0, scale 1.15 -> 1.0 over 24 frames
    sz = int(size * (1 + 0.15 * (1 - e)))
    cine(cv, t, a, b, "TIDES", CINZEL, sz, y - (sz - size) * 0.5, weight=900, track=0.14 + 0.46 * (1 - e), dur=0.0,
         blur=20, rise=0, fade=0.4, ease=expo_out, order="mid", sweep=0.55, glow=0.35, seed=2)
    if sub:
        k = smooth((t - a - 0.45) / 0.5) * (1 - smooth((t - b) / 0.3))
        if k > 0:
            yl = y + size * 1.02 + 16
            ImageDraw.Draw(cv).rectangle([W / 2 - 230 * k, yl, W / 2 + 230 * k, yl + 2], fill=(232, 190, 110, int(230 * k)))
        cine(cv, t, a + 0.6, b, "JAVA   \u00b7   BEDROCK   \u00b7   ONE OCEAN", MANROPE, 26, y + size * 1.02 + 38,
             weight=600, track=0.25, dur=0.45, blur=6, rise=4, fill=(220, 232, 242), order="lr", seed=3)
    return True

def logo(cv, t, a, b, y=300, size=190, sub=True, settle=True):
    """Bang reveal: slams in from 135% to 100% (back-out, ~10 frames) on the flash, then drifts 100->103%."""
    if not (a <= t < b + 0.3):
        return False
    base = logo_img(size)
    u = t - a
    sc = (1.35 - 0.35 * back_out(u / 0.17, 1.6)) if settle else 1.0
    sc *= 1 + 0.03 * min(u / max(b - a, 1e-3), 1)
    op = 1 - smooth((t - b) / 0.3) if b < TOTAL - 0.5 else 1.0
    op *= smooth(u / 0.05)
    im = base.resize((int(base.width * sc), int(base.height * sc)), Image.LANCZOS)
    if op < 1:
        im.putalpha(im.getchannel("A").point(lambda v: int(v * op)))
    cy = y + base.height / 2
    cv.alpha_composite(im, (int((W - im.width) / 2), int(cy - im.height / 2)))
    if sub:
        stext(cv, t, a + 0.3, b, "SURVIVAL SMP  \u2022  JAVA + BEDROCK", SANS_M, 30, y + base.height - size * 0.25,
              track=0.32, seed=4, alpha=0.95)
    return True

def pop(cv, t, a, b, m, sb, seed=3):
    """Gold in-game pop-up: scales 60% -> 110% -> 100% over ~8 frames, sparkles, subline."""
    if not (a <= t < b + 0.15):
        return False
    pop_k = back_out((t - a) / 0.135, 2.6)
    arr, _ = ptext(m, "gold", 10, "ps2p")
    im = Image.fromarray(arr)
    if pop_k < 0.999:
        sc = max(0.05, 0.6 + 0.4 * pop_k)
        im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.NEAREST)
    if t >= b:
        im.putalpha(im.getchannel("A").point(lambda v: int(v * (1 - (t - b) / 0.15))))
    cy = 330
    cv.alpha_composite(im, ((W - im.width) // 2, int(cy - im.height / 2)))
    sparkles(cv, t, a, W / 2, cy, arr.shape[1] / 2, arr.shape[0], seed=seed)
    stext(cv, t, a + 0.25, b, sb.upper(), SANS_M, 30, cy + arr.shape[0] / 2 + 18, track=0.3, seed=seed + 20)
    return True

_scrim_base = None
def _scrim(k):
    global _scrim_base
    if _scrim_base is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        _scrim_base = np.exp(-(((xx - W / 2) / (W * 0.32)) ** 2 + ((yy - 830) / 120) ** 2)) * 0.25
    im = np.zeros((H, W, 4), np.uint8)
    im[..., 3] = (_scrim_base * k * 255).astype(np.uint8)
    return Image.fromarray(im)

def overlay(t):
    cv = Image.new("RGBA", (W, H))
    drew = False
    drew |= kinetic(cv, t)
    drew |= title_card(cv, t, *TEXT["LOGO"])
    for key, seed in [("C0", 10), ("C1", 11), ("C2", 12), ("C3", 13), ("T1", 5)]:
        a, b, m, sb = TEXT[key]
        if a <= t < b + 0.25:  # soft 25% scrim behind the caption block so glints never eat letters
            k = smooth((t - a) / 0.3) * (1 - smooth((t - b) / 0.25))
            cv.alpha_composite(_scrim(k))
        drew |= cine(cv, t, a, b, m.upper(), CINZEL, 78, 760, weight=700, track=0.14, dur=0.4, blur=12, rise=8,
                     order="mid", sweep=0.35, glow=0.2, seed=seed)
        drew |= cine(cv, t, a + 0.3, b, sb.upper(), MANROPE, 26, 864, weight=600, track=0.25, dur=0.4, blur=5,
                     rise=4, fill=(225, 236, 245), alpha=0.9, seed=seed + 50)
    a, b = TEXT["POP2"][:2]
    drew |= toast(cv, t, a, b, "Challenge Complete!", "Storm Survived")
    a, b = TEXT["POP"][:2]
    drew |= toast(cv, t, a, b, "Advancement Made!", "Island Discovered")
    a, b, m, sb = TEXT["TOAST"]
    drew |= toast(cv, t, a, b, m, sb)
    drew_info = info_screen(cv, t)
    a, b = TEXT["END"]
    if a <= t:
        ImageDraw.Draw(cv).rectangle([0, 0, W, H], fill=(0, 0, 0, int(255 * smooth((t - a) / 0.35))))
        title_card(cv, t, a, b, y=230, size=170, kicker=True, sub=False)
        cine(cv, t, a + 0.35, b, "JOIN  THE  TIDE", CINZEL, 40, 480, weight=700, track=0.3, dur=0.4, blur=8,
             fill=(240, 205, 130), order="mid", seed=31)
        cine(cv, t, a + 0.5, b, "JAVA   " + JAVA, MANROPE, 40, 570, weight=700, track=0.06, dur=0.5, blur=6,
             fill=(150, 225, 255), seed=32)
        cine(cv, t, a + 0.6, b, "BEDROCK   " + BEDROCK + "   PORT " + PORT, MANROPE, 30, 640, weight=600,
             track=0.05, dur=0.5, blur=6, fill=(235, 240, 245), seed=33)
        cine(cv, t, a + 0.7, b, "Bedrock names start with a dot  (.Steve)", MANROPE, 24, 700, weight=500,
             track=0.04, dur=0.4, blur=5, fill=(200, 210, 218), alpha=0.75, seed=34)
        drew = True
    a, b = TEXT["CREDIT"]
    if a <= t < b + 0.4:
        txt = 'Music: "Neon Laser Horizon" by Kevin MacLeod (incompetech.com) - CC BY 4.0'
        f = font(MONO, 18)
        draw_text(cv, (W / 2 - f.getlength(txt) / 2, H - 60), txt, f, fill=(200, 210, 215), shadow=2,
                  alpha=smooth((t - a) / 0.5) * 0.5)
        drew = True
    if not (drew or drew_info):
        return None
    return np.asarray(cv, np.float32) / 255

def events():
    """UI sound cues: (time, kind)."""
    ev = []
    for u in (1.0, 3.4, 4.75, 6.75):
        ev.append((I0 + u, "click"))
    for t0, s, cps in [(1.3, "Tides SMP", 16), (2.0, JAVA, 24), (4.95, "Tides SMP", 18), (5.35, BEDROCK, 30), (6.25, PORT, 14)]:
        ev += [(I0 + t0 + i / cps, "key") for i in range(len(s))]
    ev += [(I0 + 3.6, "pop"), (I0 + 7.0, "pop"), (I0 + 8.05, "plip")]
    k = INFO_REF / (INFO[1] - INFO[0])
    ev = [(I0 + (t - I0) / k, kind) for t, kind in ev]
    ev += [(TEXT["TOAST"][0], "ding"), (TEXT["POP"][0], "sparkle"), (TEXT["POP2"][0], "sparkle")]
    return ev
