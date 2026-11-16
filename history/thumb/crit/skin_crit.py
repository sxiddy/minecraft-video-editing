"""Hand-shaded 64x64 skin of the Critical SMP trailer player + a 64x32 purple cape.

Ref: 4K close-ups at 27-35 s (red/black split hair, red headband, pale face, red eyes,
black hoodie with white zip, red-striped sleeves, dark striped joggers, white shoes, purple cape).
python skin_crit.py -> assets/skin_crit.png, assets/cape_crit.png
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(HERE, "assets"), exist_ok=True)
S = np.zeros((64, 64, 4), np.float32)
rng = np.random.default_rng(5)


def c(h, a=1.0):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [a], np.float32)


def regions(u, v, w, h, d):
    return {"top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d),
            "right": (u, v + d, d, h), "front": (u + d, v + d, w, h),
            "left": (u + d + w, v + d, d, h), "back": (u + 2 * d + w, v + d, w, h)}


SIDES = ("front", "right", "left", "back")


def grad(r, top, bot, noise=0.05, img=None):
    img = S if img is None else img
    x, y, w, h = r
    for j in range(h):
        t = j / max(1, h - 1)
        col = top * (1 - t) + bot * t
        for i in range(w):
            n = 1 + rng.uniform(-noise, noise)
            img[y + j, x + i, :3] = np.clip(col[:3] * n, 0, 1)
            img[y + j, x + i, 3] = col[3]


def px(r, x, y, col):
    S[r[1] + y, r[0] + x] = col


def row(r, y, col, xs=None):
    for x in (xs if xs is not None else range(r[2])):
        px(r, x, y, col)


# palette
RH0, RH1, RH2 = c("#ff2a3a"), c("#d0101f"), c("#8a0814")      # red hair
GH0, GH1, GH2 = c("#4a4650"), c("#2c2930"), c("#18161b")      # dark grey hair
BAND, BAND2 = c("#ff1e2e"), c("#a50a18")
SK0, SK1, SK2 = c("#fbf3f1"), c("#e6d9d6"), c("#c7b4b1")      # pale skin
LASH, EYE, EYE2, WH = c("#1a0a0e"), c("#ff1428"), c("#8c0010"), c("#ffffff")
R0, R1, R2, R3 = c("#ff2236"), c("#d81228"), c("#9a0a1c"), c("#5a0410")
K0, K1, K2 = c("#2a262e"), c("#18151b"), c("#0d0b0f")
ZIP, ZIP2 = c("#f4f4f8"), c("#b9b9c4")
P0, P1 = c("#3a3640"), c("#232027")                            # joggers
SH0, SH1 = c("#f2f2f6"), c("#9d9daa")
CLEAR = np.zeros(4, np.float32)

# ---------------------------------------------------------------- head base
Hd = regions(0, 0, 8, 8, 8)
for k in Hd:
    grad(Hd[k], GH1, GH2, 0.12)
# left half of the head (viewer's left on the front face) is red hair
grad((Hd["top"][0], Hd["top"][1], 4, 8), RH0, RH1, 0.12)
grad(Hd["right"], RH1, RH2, 0.12)
f = Hd["front"]
grad((f[0], f[1] + 2, 8, 6), SK0, SK1, 0.02)
face = [
    "rrrrgggg",
    "BBBBBBBB",
    "rrsssssg",
    "rLLssLLg",
    "sWEssEWs",
    "sWEssEWs",
    "ssssssss",
    "sssmmsss",
]
key = {"r": RH1, "g": GH1, "B": BAND, "s": None, "L": LASH, "E": EYE, "D": EYE2, "W": WH,
       "m": c("#b98f8b")}
for y, line in enumerate(face):
    for x, ch in enumerate(line):
        if key.get(ch) is not None:
            px(f, x, y, key[ch])
px(f, 0, 0, RH0); px(f, 2, 0, RH0); px(f, 5, 0, GH0)
for side, front_cols in (("right", range(4, 8)), ("left", range(0, 4))):
    r = Hd[side]
    for x in front_cols:
        for y in range(3, 8):
            px(r, x, y, SK1 if y < 7 else SK2)
    row(r, 1, BAND2)
for k in ("back",):
    row(Hd[k], 1, BAND)

# ---------------------------------------------------------------- hat layer: hair volume + headband
Ht = regions(32, 0, 8, 8, 8)
for k in Ht:
    x, y, w, h = Ht[k]
    S[y:y + h, x:x + w] = CLEAR
grad((Ht["top"][0], Ht["top"][1], 4, 8), RH0, RH1, 0.15)
grad((Ht["top"][0] + 4, Ht["top"][1], 4, 8), GH0, GH1, 0.15)
fr = Ht["front"]
for x in range(8):
    px(fr, x, 0, (RH0 if x % 2 else RH1) if x < 4 else (GH0 if x % 2 else GH1))
    px(fr, x, 1, BAND if x % 3 else BAND2)
for x, y in ((0, 2), (1, 2), (0, 3), (7, 2), (6, 2)):
    px(fr, x, y, RH1 if x < 4 else GH1)
for side in ("right", "left", "back"):
    r = Ht[side]
    base = (RH1, RH2) if side == "right" else (GH0, GH2)
    grad(r, base[0], base[1], 0.15)
    row(r, 1, BAND2 if side != "back" else BAND)
    if side != "back":
        front_cols = range(4, 8) if side == "right" else range(0, 4)
        for x in front_cols:
            for y in range(3, 8):
                px(r, x, y, CLEAR)
br = Ht["back"]
px(br, 3, 2, BAND); px(br, 4, 2, BAND2); px(br, 3, 3, BAND2)   # headband knot

# ---------------------------------------------------------------- body: black hoodie + white zip
B = regions(16, 16, 8, 12, 4)
for k in B:
    grad(B[k], K0, K2, 0.06)
bf = B["front"]
for y in range(12):
    px(bf, 3, y, ZIP if y % 4 else ZIP2)
    px(bf, 4, y, K2)
for k in SIDES:
    r = B[k]
    for x in range(r[2]):
        if k == "front" and x in (3, 4):
            continue
        for yy, col in ((2, R1), (3, R2), (6, R1), (10, R2)):
            if k == "front" and 1 < x < 6 and yy > 3:
                continue
            px(r, x, yy, col)

# jacket layer: thin hood rim + bottom hem only (keeps the zip readable)
J = regions(16, 32, 8, 12, 4)
for k in J:
    x, y, w, h = J[k]
    S[y:y + h, x:x + w] = CLEAR
for k in SIDES:
    row(J[k], 11, K2)
row(J["front"], 0, K0, [0, 1, 6, 7])
grad((J["back"][0] + 1, J["back"][1], 6, 3), K0, K1, 0.1)

# ---------------------------------------------------------------- arms: striped upper, red lower, white cuff
for (bu, bv), (ou, ov) in (((40, 16), (40, 32)), ((32, 48), (48, 48))):
    Ab = regions(bu, bv, 4, 12, 4)
    for k in Ab:
        grad(Ab[k], K0, K1, 0.05)
        if k in SIDES:
            for xx in range(4):
                for yy in (1, 3, 5):
                    px(Ab[k], xx, yy, R1 if yy != 5 else R2)
            grad((Ab[k][0], Ab[k][1] + 6, 4, 4), R0, R2, 0.06)
            for xx in range(4):
                px(Ab[k], xx, 10, ZIP)
                px(Ab[k], xx, 11, SK1)
    grad(Ab["bottom"], SK1, SK2, 0.03)
    grad(Ab["top"], K0, K1, 0.05)
    Ao = regions(ou, ov, 4, 12, 4)
    for k in Ao:
        x, y, w, h = Ao[k]
        S[y:y + h, x:x + w] = CLEAR
    for k in SIDES:   # sleeve hem on the outer layer for depth
        for xx in range(4):
            px(Ao[k], xx, 9, R3)
            px(Ao[k], xx, 0, K0)

# ---------------------------------------------------------------- legs: dark joggers + red stripes + white shoes
for (bu, bv) in ((0, 16), (16, 48)):
    L = regions(bu, bv, 4, 12, 4)
    for k in L:
        grad(L[k], P0, P1, 0.08)
        if k in SIDES:
            for xx in range(4):
                px(L[k], xx, 1, R1); px(L[k], xx, 2, R2)
                px(L[k], xx, 5, R1)
                px(L[k], xx, 8, K2)
                px(L[k], xx, 9, SH0); px(L[k], xx, 10, SH0); px(L[k], xx, 11, SH1)
    x, y, w, h = L["bottom"]
    S[y:y + h, x:x + w] = SH1

img = Image.fromarray((np.clip(S, 0, 1) * 255).astype(np.uint8), "RGBA")
img.save(os.path.join(HERE, "assets", "skin_crit.png"))
img.resize((512, 512), Image.NEAREST).save(os.path.join(HERE, "assets", "skin_crit_preview.png"))

# ---------------------------------------------------------------- cape 64x32 (front face at 1,1 10x16)
C = np.zeros((32, 64, 4), np.float32)
CP0, CP1, CP2, CPH = c("#c58be6"), c("#a46ad0"), c("#7a45a8"), c("#ead2ff")
for (x, y, w, h) in ((1, 1, 10, 16), (12, 1, 10, 16), (0, 1, 1, 16), (11, 1, 1, 16), (1, 0, 10, 1), (11, 0, 10, 1)):
    grad((x, y, w, h), CP0, CP2, 0.06, img=C)
for (x, y) in ((4, 4), (5, 3), (6, 4), (5, 5), (5, 4), (3, 9), (7, 11), (2, 13), (8, 6), (4, 14), (8, 14)):
    for ox in (1, 12):
        C[1 + y, ox + x - 1] = CPH
cimg = Image.fromarray((np.clip(C, 0, 1) * 255).astype(np.uint8), "RGBA")
cimg.save(os.path.join(HERE, "assets", "cape_crit.png"))
print("ok")
