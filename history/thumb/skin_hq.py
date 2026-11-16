"""Hand-shaded 64x64 Minecraft skin (base + outer layer) matching the Tides footage player.

python skin_hq.py -> assets/skin_hq.png (+ an 8x preview)
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
S = np.zeros((64, 64, 4), np.float32)
rng = np.random.default_rng(11)


def c(h, a=1.0):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [a], np.float32)


def regions(u, v, w, h, d):
    return {"top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d),
            "right": (u, v + d, d, h), "front": (u + d, v + d, w, h),
            "left": (u + d + w, v + d, d, h), "back": (u + 2 * d + w, v + d, w, h)}


SIDES = ("front", "right", "left", "back")


def grad(r, top, bot, noise=0.05):
    x, y, w, h = r
    for j in range(h):
        t = j / max(1, h - 1)
        col = top * (1 - t) + bot * t
        for i in range(w):
            n = 1 + rng.uniform(-noise, noise)
            S[y + j, x + i, :3] = np.clip(col[:3] * n, 0, 1)
            S[y + j, x + i, 3] = col[3]


def px(r, x, y, col):
    S[r[1] + y, r[0] + x] = col


def row(r, y, col, xs=None):
    for x in (xs if xs is not None else range(r[2])):
        px(r, x, y, col)


# palette
H0, H1, H2, H3 = c("#0e090d"), c("#1b1218"), c("#2a1c25"), c("#47303d")
PK, PK2 = c("#ff3fa4"), c("#ff9ad3")
S0, S1, S2 = c("#e9b48e"), c("#d49a74"), c("#b07656")
LASH, IR1, IR2, HL = c("#1a0f18"), c("#0fb4d8"), c("#47e6ff"), c("#ffffff")
R0, R1, R2, R3 = c("#e8233a"), c("#c0102c"), c("#82081c"), c("#4e0412")
K0, K1, K2 = c("#2a2430"), c("#1a161e"), c("#0f0c12")
SH0, SH1 = c("#f0f0f5"), c("#9a9aa6")
CLEAR = np.zeros(4, np.float32)

# ---------------------------------------------------------------- head (base)
Hd = regions(0, 0, 8, 8, 8)
for k in Hd:
    grad(Hd[k], H2, H1, 0.12)
f = Hd["front"]
grad((f[0], f[1] + 2, 8, 6), S0, S1, 0.03)
face = [
    "23233PQ2",
    "1213211Q",
    "11s1ss11",
    "1LssssL1",
    "sLLssLLs",
    "sWIssIWs",
    "sIIssIIs",
    "sssmmsss",
]
key = {"1": H1, "2": H2, "3": H3, "P": PK, "Q": PK2, "s": None, "L": LASH, "W": IR2, "I": IR1,
       "b": c("#f2a39a"), "m": c("#a3554c"), ".": None}
for y, line in enumerate(face):
    for x, ch in enumerate(line):
        if key.get(ch) is not None:
            px(f, x, y, key[ch])
px(f, 7, 6, S1)
# sides: hair at the back and top, skin + ear at the front-bottom
for side, front_cols, ear in (("right", range(4, 8), 5), ("left", range(0, 4), 2)):
    r = Hd[side]
    for x in front_cols:
        for y in range(3, 8):
            px(r, x, y, S1 if y < 7 else S2)
    px(r, ear, 4, S2); px(r, ear, 5, S2)
    for y in range(0, 3):
        for x in range(8):
            px(r, x, y, H2 if (x + y) % 3 else H3)
row(Hd["top"], 7, PK, [5, 6]); row(Hd["top"], 6, PK2, [5]); row(Hd["top"], 5, PK, [6])

# ---------------------------------------------------------------- hat layer: hair volume
Ht = regions(32, 0, 8, 8, 8)
for k in Ht:
    x, y, w, h = Ht[k]
    S[y:y + h, x:x + w] = CLEAR
grad(Ht["top"], H3, H2, 0.15)
row(Ht["top"], 7, PK, [5, 6]); row(Ht["top"], 6, PK, [6])
grad(Ht["back"], H2, H0, 0.15)
fr = Ht["front"]
for x in range(8):
    px(fr, x, 0, H3 if x % 3 else H2)
for x in (0, 1, 2, 4, 6, 7):
    px(fr, x, 1, H2)
for x in (0, 3, 7):
    px(fr, x, 2, H1)
px(fr, 6, 0, PK); px(fr, 6, 1, PK); px(fr, 6, 2, PK2)
for side, back_cols in (("right", range(0, 4)), ("left", range(4, 8))):
    r = Ht[side]
    for x in range(8):
        px(r, x, 0, H3)
        px(r, x, 1, H2)
    for x in back_cols:
        for y in range(2, 7):
            px(r, x, y, H1 if (x + y) % 2 else H2)

# ---------------------------------------------------------------- body base: black tee
B = regions(16, 16, 8, 12, 4)
for k in B:
    grad(B[k], K0, K2, 0.06)
px(B["front"], 3, 3, PK); px(B["front"], 4, 3, PK); px(B["front"], 3, 4, PK2); px(B["front"], 4, 4, PK)

# ---------------------------------------------------------------- jacket layer: open red hoodie
J = regions(16, 32, 8, 12, 4)
for k in J:
    grad(J[k], R0, R2, 0.07)
jf = J["front"]
for y in range(12):
    for x in (3, 4):
        px(jf, x, y, CLEAR)
for y in range(1, 12):   # shading along the zip edge
    px(jf, 2, y, R2); px(jf, 5, y, R2)
row(jf, 0, R3)
for y in (1, 2, 3, 4):
    px(jf, 2, y, PK if y < 4 else PK2); px(jf, 5, y, PK if y < 4 else PK2)
for k in SIDES:
    r = J[k]
    for x in range(r[2]):
        if not (k == "front" and x in (3, 4)):
            px(r, x, 6, K1)
            px(r, x, 7, R3)
            px(r, x, 11, R3)
row(jf, 9, R3, [0, 1, 6, 7])
gb = J["back"]
for y in range(0, 4):   # hood
    for x in range(1, 7):
        px(gb, x, y, R2 if y < 3 else R3)

# ---------------------------------------------------------------- arms: skin base + red sleeve layer
for (bu, bv), (ou, ov) in (((40, 16), (40, 32)), ((32, 48), (48, 48))):
    Ab = regions(bu, bv, 4, 12, 4)
    for k in Ab:
        grad(Ab[k], K0, K1, 0.05)
        x, y, w, h = Ab[k]
        if k in SIDES:
            grad((x, y + 10, w, 2), S1, S2, 0.04)
    grad(Ab["bottom"], S1, S2, 0.04)
    Ao = regions(ou, ov, 4, 12, 4)
    for k in Ao:
        grad(Ao[k], R0, R2, 0.08)
        if k in SIDES:
            x, y, w, h = Ao[k]
            for xx in range(w):
                px(Ao[k], xx, 3, K1); px(Ao[k], xx, 6, K1)
                px(Ao[k], xx, 9, PK)
                px(Ao[k], xx, 10, CLEAR); px(Ao[k], xx, 11, CLEAR)
    x, y, w, h = Ao["bottom"]
    S[y:y + h, x:x + w] = CLEAR

# ---------------------------------------------------------------- legs: black joggers + sneakers
for (bu, bv) in ((0, 16), (16, 48)):
    L = regions(bu, bv, 4, 12, 4)
    for k in L:
        grad(L[k], K0, K2, 0.06)
        if k in SIDES:
            x, y, w, h = L[k]
            for xx in range(w):
                px(L[k], xx, 2, R1); px(L[k], xx, 3, R2)
                px(L[k], xx, 9, K2)
                px(L[k], xx, 10, SH0); px(L[k], xx, 11, SH1)
    px(L["front"], 1, 10, PK)
    x, y, w, h = L["bottom"]
    S[y:y + h, x:x + w] = SH1

img = Image.fromarray((np.clip(S, 0, 1) * 255).astype(np.uint8), "RGBA")
img.save(os.path.join(HERE, "assets", "skin_hq.png"))
img.resize((512, 512), Image.NEAREST).save(os.path.join(HERE, "..", "analysis", "skin_hq_preview.png"))
print("ok")
