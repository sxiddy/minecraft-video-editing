"""Pixel-art type like the client reference (RuneSpire): glyphs rendered on the font's native pixel grid,
nearest-neighbour upscaled, a hard-banded gradient (one flat colour per pixel row), a thin outline and a drop shadow.

render(text, style, px) -> RGBA uint8 numpy array.  px = screen pixels per font pixel.
"""
import pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FD = pathlib.Path(__file__).parent / "assets" / "fonts" / "pixel"
FONTS = {  # name: (file, native em size in px, cap height in font pixels)
    "mono": (FD / "ttf" / "Monocraft-ttf" / "Monocraft.ttf", 9, 7),
    "ps2p": (FD / "PressStart2P.ttf", 8, 8),
}
# colour bands top -> bottom (one per font-pixel row of the cap height; repeated/clamped otherwise)
STYLES = {
    "logo":  dict(font="mono", bands=["#FFFFFF", "#E4F6FF", "#B5E3FF", "#7CC7F5", "#4AA2E6", "#2F7AD0", "#2460B4"],
                  outline="#E7B04C", shadow="#06101E", inner="#1B3F86"),
    "gold":  dict(font="mono", bands=["#FFF7D6", "#FFE9A0", "#FFD466", "#FFBE3A", "#F6A322", "#E58A16", "#C96E0E"],
                  outline="#3A1E06", shadow="#140A02", inner="#8A4A06"),
    "aqua":  dict(font="mono", bands=["#F2FFFF", "#C8F6FF", "#8EE6F7", "#55D0EA", "#2FB4D8", "#1E93BE", "#167AA3"],
                  outline="#0B2C44", shadow="#03101A", inner="#0E5878"),
    "white": dict(font="mono", bands=["#FFFFFF"], outline=None, shadow="#1A1A1A", inner=None),
    "cyan":  dict(font="mono", bands=["#B8ECFF"], outline=None, shadow="#0A2430", inner=None),
}

def _hex(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)

def _char_mask(ch, fnt, em, bold):
    im = Image.new("L", (em * 2, em * 2), 0)
    ImageDraw.Draw(im).text((2, 2), ch, font=fnt, fill=255)
    m = np.asarray(im) > 127
    if bold:  # Minecraft bold: the glyph again one pixel to the right
        m = m | np.roll(m, 1, axis=1)
    return m

def glyph_spans(text, font="mono", bold=False, gap=1):
    """Native-pixel x range [x0, x1) of each character in glyph_mask's layout (spaces get their gap cell)."""
    f, em, cap = FONTS[font]
    fnt = ImageFont.truetype(str(f), em)
    space, x, out = max(2, em // 2), 0, []
    for ch in text:
        cols = [] if ch == " " else np.where(_char_mask(ch, fnt, em, bold).any(0))[0]
        if len(cols) == 0:
            out.append((x, x + space)); x += space; continue
        w = cols[-1] - cols[0] + 1
        out.append((x, x + w)); x += w + gap
    return out

def glyph_mask(text, font="mono", bold=False, gap=1):
    """Binary mask at native resolution (True = ink). Laid out per letter: each glyph's own width + `gap` px,
    so letters never touch (the reference keeps a clean 1-2 px gap between letters)."""
    f, em, cap = FONTS[font]
    fnt = ImageFont.truetype(str(f), em)
    space = max(2, em // 2)
    cells = []
    for ch in text:
        if ch == " ":
            cells.append(np.zeros((em * 2, space), bool)); continue
        m = _char_mask(ch, fnt, em, bold)
        cols = np.where(m.any(0))[0]
        if len(cols) == 0:
            cells.append(np.zeros((em * 2, space), bool)); continue
        cells.append(m[:, cols[0]:cols[-1] + 1])
        cells.append(np.zeros((em * 2, gap), bool))
    m = np.hstack(cells)
    rows = np.where(m.any(1))[0]
    return m[rows[0]:rows[-1] + 1]

PAD = 3

def render(text, style="logo", px=12, bold=False, outline_px=None, shadow_off=(1.0, 1.0), font=None):
    st = dict(STYLES[style])
    if font:
        st["font"] = font
    m = glyph_mask(text, st["font"], bold)
    h, w = m.shape
    pad = PAD
    M = np.zeros((h + 2 * pad, w + 2 * pad), bool)
    M[pad:pad + h, pad:pad + w] = m
    big = np.kron(M, np.ones((px, px), bool))  # nearest-neighbour upscale
    H, W = big.shape
    out = np.zeros((H, W, 4), np.uint8)
    # drop shadow: the outlined shape, offset down-right
    ol = outline_px if outline_px is not None else max(2, px // 3)
    shape = big
    if st["outline"]:
        k = ol
        sh = np.zeros_like(big)
        for dy in range(-k, k + 1):
            for dx in range(-k, k + 1):
                sh |= np.roll(np.roll(big, dy, 0), dx, 1)
        shape = sh
    if st["shadow"]:
        oy, ox = int(px * shadow_off[1]), int(px * shadow_off[0])
        s = np.roll(np.roll(shape, oy, 0), ox, 1)
        out[s] = (*_hex(st["shadow"]), 200)
    if st["outline"]:
        out[shape] = (*_hex(st["outline"]), 255)
    # banded fill: one flat colour per font-pixel row
    bands = [_hex(c) for c in st["bands"]]
    rows = np.arange(H) // px - pad
    idx = np.clip((rows * len(bands)) // max(h, 1), 0, len(bands) - 1)
    fill = np.stack([bands[i] for i in idx])[:, None, :].repeat(W, 1)
    out[big, :3] = fill[big]
    out[big, 3] = 255
    # inner shade: the bottom font-pixel edge of each stroke a touch darker (the reference's 1px shading line)
    if st["inner"] and False:  # disabled: read as stray lines at this size
        below = np.roll(M, -1, 0) == False  # noqa: E712
        edge = M & below
        e = np.kron(edge, np.ones((px, px), bool))
        e &= (np.arange(H) % px >= px * 2 // 3)[:, None]
        out[e & big, :3] = _hex(st["inner"])
    return out

if __name__ == "__main__":
    import sys
    bg = Image.new("RGBA", (1920, 1080), (40, 70, 90, 255))
    y = 60
    for txt, sty, px, bold in [("TIDES SMP", "logo", 26, False), ("ISLAND DISCOVERED!", "gold", 11, False),
                               ("SURVIVE THE OPEN SEA", "aqua", 10, False), ("every island is earned", "white", 6, False),
                               ("play: pm-twirl.gl.joinmc.link", "cyan", 7, False)]:
        a = render(txt, sty, px, bold)
        bg.alpha_composite(Image.fromarray(a), ((1920 - a.shape[1]) // 2, y))
        y += a.shape[0] + 40
    bg.convert("RGB").save(sys.argv[1] if len(sys.argv) > 1 else "pixel_test.png")
