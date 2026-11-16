"""Blender: full 3D Tides SMP thumbnail scene (character, raft, blocky ocean, sunset).

blender -b -P scene3d.py -- [out.png] [percent]
"""
import bpy, bmesh, math, os, random, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else os.path.join(HERE, "assets", "scene3d.png")
PCT = int(argv[1]) if len(argv) > 1 else 100
CHAR = len(argv) > 2 and argv[2] in ("char", "hero")
HERO = len(argv) > 2 and argv[2] == "hero"
from mathutils import Vector
rng = random.Random(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
for kind in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = kind
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = "GPU"
        break
    except Exception:
        pass
sc.cycles.samples = 128
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.resolution_percentage = PCT
sc.render.image_settings.file_format = "PNG"
sc.view_settings.view_transform = "AgX"
try:
    sc.view_settings.look = "AgX - Punchy"
except TypeError:
    pass


def hexc(h, a=1.0):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return (*[c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb], a)


def srgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [1.0])


# ---------------------------------------------------------------- pixel textures
def make_image(name, arr):
    """arr: HxWx4 sRGB floats, row 0 = top."""
    h, w = arr.shape[:2]
    img = bpy.data.images.new(name, w, h, alpha=True)
    img.pixels = np.flipud(arr).ravel().tolist()
    img.pack()
    return img


def noisy(arr, amt=0.07, seed=1):
    r = np.random.default_rng(seed)
    n = 1 + r.uniform(-amt, amt, arr.shape[:2])[..., None]
    out = arr.copy()
    out[..., :3] = np.clip(arr[..., :3] * n, 0, 1)
    return out


def pixel_material(name, img, rough=0.75, emit=None, emit_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img
    t.interpolation = "Closest"
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    if emit is not None:
        e = nt.nodes.new("ShaderNodeTexImage")
        e.image = emit
        e.interpolation = "Closest"
        nt.links.new(e.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit_strength
    return m


# Minecraft 64x64 skin
S = np.zeros((64, 64, 4))
HAIR, HAIR2 = srgb("#1d1519"), srgb("#2c2026")
PINK, PINK2 = srgb("#ff3fa4"), srgb("#ff8fd0")
SKIN, SKIN2 = srgb("#efbb94"), srgb("#d99c74")
RED, RED2, BLK = srgb("#e01632"), srgb("#9c0c20"), srgb("#141217")
WHITE, EYE = srgb("#f7f7f7"), srgb("#3a1630")


def regions(u, v, w, h, d):
    return {"top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d),
            "right": (u, v + d, d, h), "front": (u + d, v + d, w, h),
            "left": (u + d + w, v + d, d, h), "back": (u + 2 * d + w, v + d, w, h)}


def fill(r, c):
    x, y, w, h = r
    S[y:y + h, x:x + w] = c


def px(r, x, y, c):
    S[r[1] + y, r[0] + x] = c


# head
H = regions(0, 0, 8, 8, 8)
for k in H.values():
    fill(k, HAIR)
f = H["front"]
for y in range(2, 8):
    for x in range(8):
        px(f, x, y, SKIN)
for x in (0, 7):
    for y in (2, 3):
        px(f, x, y, HAIR)
px(f, 1, 2, HAIR); px(f, 6, 2, HAIR); px(f, 5, 2, PINK); px(f, 5, 1, PINK); px(f, 4, 1, PINK2)
# angry brows + eyes + open shout
for x, y in ((1, 3), (2, 3), (5, 3), (6, 3)):
    px(f, x, y, BLK)
px(f, 1, 4, WHITE); px(f, 2, 4, EYE); px(f, 5, 4, EYE); px(f, 6, 4, WHITE)
for x in range(2, 6):
    px(f, x, 6, srgb("#5a0d1a"))
px(f, 3, 7, srgb("#5a0d1a")); px(f, 4, 7, srgb("#5a0d1a")); px(f, 3, 5, SKIN2); px(f, 4, 5, SKIN2)
for side, front_cols in (("right", range(4, 8)), ("left", range(0, 4))):
    r = H[side]
    for x in front_cols:
        for y in range(4, 8):
            px(r, x, y, SKIN)
for x in (2, 3, 4):
    px(H["top"], x, 7, PINK); px(H["top"], x + 1, 6, PINK)
# body
B = regions(16, 16, 8, 12, 4)
for k in B.values():
    fill(k, RED)
for k in ("front", "back", "left", "right"):
    x, y, w, h = B[k]
    S[y + 0, x:x + w] = BLK
    S[y + 4, x:x + w] = BLK
    S[y + 7, x:x + w] = RED2
    S[y + 9, x:x + w] = BLK
    S[y + 10:y + 12, x:x + w] = BLK
f = B["front"]
for y in range(1, 9):
    px(f, 3, y, BLK); px(f, 4, y, BLK)
px(f, 3, 9, PINK); px(f, 4, 9, PINK); px(f, 3, 2, PINK2)
# arms (right 40,16 ; left 32,48) and legs (right 0,16 ; left 16,48)
for u, v in ((40, 16), (32, 48)):
    A = regions(u, v, 4, 12, 4)
    for k in A.values():
        fill(k, RED)
    for k in ("front", "back", "left", "right"):
        x, y, w, h = A[k]
        S[y + 0, x:x + w] = BLK
        S[y + 3, x:x + w] = BLK
        S[y + 6, x:x + w] = BLK
        S[y + 9, x:x + w] = PINK
        S[y + 10:y + 12, x:x + w] = SKIN
    fill(A["bottom"], SKIN)
for u, v in ((0, 16), (16, 48)):
    L = regions(u, v, 4, 12, 4)
    for k in L.values():
        fill(k, BLK)
    for k in ("front", "back", "left", "right"):
        x, y, w, h = L[k]
        S[y + 3, x:x + w] = RED
        S[y + 4, x:x + w] = RED2
        S[y + 10, x:x + w] = srgb("#2f2f36")
        S[y + 11, x:x + w] = WHITE
    fill(L["bottom"], srgb("#2f2f36"))
skin_img = bpy.data.images.load(os.path.join(HERE, "assets", "skin_hq.png"))
skin_img.pack()
skin_mat = pixel_material("skin", skin_img, 0.7)
_n = skin_mat.node_tree.nodes
_tex = [n for n in _n if n.type == "TEX_IMAGE"][0]
skin_mat.node_tree.links.new(_tex.outputs["Alpha"], _n["Principled BSDF"].inputs["Alpha"])


def tex16(fn, seed):
    a = np.zeros((16, 16, 4))
    for y in range(16):
        for x in range(16):
            a[y, x] = fn(x, y)
    return noisy(a, 0.1, seed)


PLANK = srgb("#b08a52")


def plank(x, y):
    if y % 4 == 3:
        return srgb("#6e5130")
    if (x + (y // 4) * 5) % 16 == 0:
        return srgb("#7f5e36")
    return PLANK if (x * 7 + y) % 5 else srgb("#9d7745")


def table_top(x, y):
    if x in (0, 15) or y in (0, 15):
        return srgb("#5d3e22")
    if x in (5, 10) or y in (5, 10):
        return srgb("#4a2f18")
    return srgb("#9c6c3c") if (x + y) % 3 else srgb("#86592f")


def table_side(x, y):
    if y < 3:
        return srgb("#5d3e22") if y == 2 else srgb("#9c6c3c")
    if 4 <= x <= 6 and 5 <= y <= 12:
        return srgb("#8c8c8c") if y > 6 else srgb("#6d4a2a")   # saw / hammer
    if 9 <= x <= 12 and 6 <= y <= 8:
        return srgb("#a4a4a4")
    return plank(x, y)


def stone(x, y):
    v = (x * 13 + y * 7 + (x * y) % 5) % 6
    return srgb(["#8a8a8a", "#7b7b7b", "#969696", "#6e6e6e", "#858585", "#909090"][v])


def furnace_front(x, y):
    if 3 <= x <= 12 and 8 <= y <= 13:
        return srgb("#ffb028") if y > 10 else (srgb("#ff6a10") if (x + y) % 2 else srgb("#ffd25a"))
    if 3 <= x <= 12 and 2 <= y <= 5:
        return srgb("#3a3a3a")
    return stone(x, y)


def furnace_emit(x, y):
    if 3 <= x <= 12 and 8 <= y <= 13:
        return furnace_front(x, y)
    return np.array([0, 0, 0, 1.0])


IMG = {k: make_image(k, tex16(fn, i)) for i, (k, fn) in enumerate([
    ("plank", plank), ("ttop", table_top), ("tside", table_side), ("stone", stone),
    ("ffront", furnace_front), ("femit", furnace_emit)])}
MAT = {k: pixel_material(k, IMG[k]) for k in ("plank", "ttop", "tside", "stone")}
MAT["ffront"] = pixel_material("ffront", IMG["ffront"], emit=IMG["femit"], emit_strength=6)


# ---------------------------------------------------------------- box builder
def box(name, x0, x1, y0, y1, z0, z1, uvs=None, mats=None, parent=None, loc=(0, 0, 0)):
    """uvs: dict face->(u,v,w,h) pixel rect in a 64x64 atlas; mats: dict face->material."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    V = {}
    for x in (x0, x1):
        for y in (y0, y1):
            for z in (z0, z1):
                V[(x, y, z)] = bm.verts.new((x, y, z))
    # corners listed TL, TR, BR, BL in image space
    faces = {
        "front": [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)],
        "back": [(x1, y1, z1), (x0, y1, z1), (x0, y1, z0), (x1, y1, z0)],
        "right": [(x0, y1, z1), (x0, y0, z1), (x0, y0, z0), (x0, y1, z0)],
        "left": [(x1, y0, z1), (x1, y1, z1), (x1, y1, z0), (x1, y0, z0)],
        "top": [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
        "bottom": [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)],
    }
    uvl = bm.loops.layers.uv.new()
    order = list(faces)
    mat_list = []
    for fname in order:
        cs = faces[fname]
        fa = bm.faces.new([V[c] for c in cs])
        if mats:
            m = mats[fname]
            if m not in mat_list:
                mat_list.append(m)
            fa.material_index = mat_list.index(m)
        if uvs:
            u, v, w, h = uvs[fname]
            size = 64.0
            uvc = [(u / size, 1 - v / size), ((u + w) / size, 1 - v / size),
                   ((u + w) / size, 1 - (v + h) / size), (u / size, 1 - (v + h) / size)]
        else:
            uvc = [(0, 1), (1, 1), (1, 0), (0, 0)]
        lookup = {tuple(V[c].co): uvc[i] for i, c in enumerate(cs)}
        for lp in fa.loops:
            lp[uvl].uv = lookup[tuple(lp.vert.co)]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    for m in mat_list:
        me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    o.location = loc
    if parent:
        o.parent = parent
    return o


def block(name, loc, mats):
    return box(name, -.5, .5, -.5, .5, -.5, .5, mats=mats, loc=loc)


def same(m):
    return {k: m for k in ("front", "back", "left", "right", "top", "bottom")}


# ---------------------------------------------------------------- character
P = 1 / 16.0


def part(name, uv_origin, w, h, d, offs, pivot, parent, rot, inflate=0.0):
    x0, y0, z0 = offs
    e = inflate
    o = box(name, (x0 - e) * P, (x0 + w + e) * P, (y0 - e) * P, (y0 + d + e) * P,
            (z0 - e) * P, (z0 + h + e) * P, uvs=regions(*uv_origin, w, h, d),
            mats=same(skin_mat), parent=parent, loc=[c * P for c in pivot])
    o.rotation_euler = [math.radians(a) for a in rot]
    if inflate == 0.0:
        bv = o.modifiers.new("bevel", "BEVEL"); bv.width = 0.25 * P; bv.segments = 2
        o.modifiers.new("ws", "WEIGHTED_NORMAL")
    return o


def overlay(base, uv_origin, w, h, d, offs, amount):
    o = part(base.name + "_ov", uv_origin, w, h, d, offs, (0, 0, 0), base, (0, 0, 0), inflate=amount)
    return o


rig = bpy.data.objects.new("rig", None)
sc.collection.objects.link(rig)
rig.location = (0.55, 0.9, 0.62 + 12 * P + 0.25)   # mid-jump above the raft
rig.scale = (1.12, 1.12, 1.12)
rig.rotation_euler = (math.radians(-8), math.radians(6), math.radians(-22))
body = part("body", (16, 16), 8, 12, 4, (-4, -2, 0), (0, 0, 0), rig, (0, 0, 0))
head = part("head", (0, 0), 8, 8, 8, (-4, -4, 0), (0, 0, 12), rig, (6, -4, -4))
arm_r = part("arm_r", (40, 16), 4, 12, 4, (-2, -2, -10), (-6, 0, 10), rig, (-168, -28, 0))
arm_l = part("arm_l", (32, 48), 4, 12, 4, (-2, -2, -10), (6, 0, 10), rig, (35, 0, 30))
leg_r = part("leg_r", (0, 16), 4, 12, 4, (-2, -2, -12), (-2, 0, 0), rig, (-38, 0, -8))
leg_l = part("leg_l", (16, 48), 4, 12, 4, (-2, -2, -12), (2, 0, 0), rig, (28, 0, 8))
overlay(head, (32, 0), 8, 8, 8, (-4, -4, 0), 0.5)
overlay(body, (16, 32), 8, 12, 4, (-4, -2, 0), 0.25)
overlay(arm_r, (40, 32), 4, 12, 4, (-2, -2, -10), 0.25)
overlay(arm_l, (48, 48), 4, 12, 4, (-2, -2, -10), 0.25)

# pink sword, voxel-extruded 16x16 item sprite, held in the right hand
sword_px = {}
for t in range(4, 15):
    sword_px[(t, 15 - t)] = "#ff4fb0"
    sword_px[(t + 1, 15 - t)] = "#b0177a" if t < 14 else None
    sword_px[(t, 14 - t)] = "#ffd1ec"
    if t < 14:
        sword_px[(t + 1, 16 - t)] = "#5c0a3c"
    sword_px[(t - 1, 14 - t)] = "#5c0a3c"
for k in [k for k, v in sword_px.items() if v is None]:
    del sword_px[k]
for a in range(1, 6):   # guard
    sword_px[(a, 15 - (6 - a))] = "#3b2b55"
for t in range(0, 4):   # grip
    sword_px[(t, 15 - t)] = "#5a3a1e"
sword_px[(0, 15)] = "#3b2b55"
smat = {}
sword = bpy.data.objects.new("sword", None)
sc.collection.objects.link(sword)
sword.parent = arm_r
sword.location = (0, -1 * P, -10 * P)
sword.rotation_euler = (0, math.radians(135), 0)
sp = 1.35 / 16
for (x, y), col in sword_px.items():
    if col not in smat:
        m = bpy.data.materials.new(col)
        m.use_nodes = True
        bs = m.node_tree.nodes["Principled BSDF"]
        bs.inputs["Base Color"].default_value = hexc(col)
        bs.inputs["Roughness"].default_value = 0.35
        if col.startswith("#ff"):
            bs.inputs["Emission Color"].default_value = hexc(col)
            bs.inputs["Emission Strength"].default_value = 1.5
        smat[col] = m
    gx, gy = x - 2, (15 - y) - 2      # grip near the origin
    box("sw", gx * sp, (gx + 1) * sp, -sp / 2, sp / 2, gy * sp, (gy + 1) * sp,
        mats=same(smat[col]), parent=sword)

# ---------------------------------------------------------------- raft + props
TOP = 0.62   # raft deck height
for i in range(-1, 3):
    for j in range(0, 3):
        block(f"raft{i}{j}", (i, 1 + j, TOP - 0.5), same(MAT["plank"]))
tmats = {k: MAT["tside"] for k in ("front", "back", "left", "right")}
tmats.update(top=MAT["ttop"], bottom=MAT["plank"])
ct = block("crafting", (1.0, 2.6, TOP + 0.5), tmats)
ct.rotation_euler[2] = math.radians(-12)
fm = {k: MAT["stone"] for k in ("back", "left", "right", "top", "bottom")}
fm["front"] = MAT["ffront"]
fu = block("furnace", (2.15, 3.0, TOP + 0.5), fm)
fu.rotation_euler[2] = math.radians(-25)
fu.location = (2.2, 2.4, TOP + 0.5)
fl = bpy.data.lights.new("fire", "POINT"); fl.energy = 60; fl.color = (1, 0.5, 0.15)
flo = bpy.data.objects.new("fire", fl); flo.location = (1.95, 2.4, TOP + 0.35); sc.collection.objects.link(flo)

# ---------------------------------------------------------------- blocky ocean
water = bpy.data.materials.new("water")
water.use_nodes = True
nt = water.node_tree
wb = nt.nodes["Principled BSDF"]
attr = nt.nodes.new("ShaderNodeAttribute"); attr.attribute_name = "col"
nt.links.new(attr.outputs["Color"], wb.inputs["Base Color"])
wb.inputs["Roughness"].default_value = 0.3
wb.inputs["Specular IOR Level"].default_value = 0.25
nt.links.new(attr.outputs["Color"], wb.inputs["Emission Color"])
wb.inputs["Emission Strength"].default_value = 0.35
wb.inputs["Coat Weight"].default_value = 0.4

me = bpy.data.meshes.new("ocean")
bm = bmesh.new()
colL = bm.loops.layers.color.new("col")
NX0, NX1, NY0, NY1 = -45, 45, -12, 90
step = 0.125


def wave(x, y):
    h = (0.32 * math.sin(x * 0.45 + y * 0.18) + 0.22 * math.sin(y * 0.6 - x * 0.2 + 1.3)
         + 0.12 * math.sin(x * 1.3 + y * 0.9))
    h *= min(1.0, 0.35 + abs(y - 2) / 8)   # calmer right around the raft
    return round(h / step) * step


hmap = {(i, j): wave(i, j) for i in range(NX0, NX1) for j in range(NY0, NY1)}


def wcol(h, i, j):
    base = np.array([0.05, 0.42, 0.85]) if (i + j) % 2 else np.array([0.07, 0.48, 0.9])
    crest = np.clip((h - 0.15) / 0.4, 0, 1)
    c = base * (1 - crest) + np.array([0.45, 0.85, 0.95]) * crest
    c *= 1 + rng.uniform(-0.08, 0.08)
    return (*c, 1.0)


def quad(vs, col):
    f = bm.faces.new([bm.verts.new(v) for v in vs])
    for lp in f.loops:
        lp[colL] = col
    return f


for (i, j), h in hmap.items():
    c = wcol(h, i, j)
    quad([(i - .5, j - .5, h), (i + .5, j - .5, h), (i + .5, j + .5, h), (i - .5, j + .5, h)], c)
    side = tuple(v * 0.45 for v in c[:3]) + (1.0,)
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        hn = hmap.get((i + di, j + dj), -1.0)
        if hn < h:
            if di:
                x = i + di * .5
                vs = [(x, j - .5, hn), (x, j + .5, hn), (x, j + .5, h), (x, j - .5, h)]
            else:
                y = j + dj * .5
                vs = [(i - .5, y, hn), (i + .5, y, hn), (i + .5, y, h), (i - .5, y, h)]
            quad(vs, side)
bm.to_mesh(me)
bm.free()
me.materials.append(water)
ocean = bpy.data.objects.new("ocean", me)
sc.collection.objects.link(ocean)
# keep the raft footprint flat-ish water
ocean.location.z = -0.05

# ---------------------------------------------------------------- sky, sun, clouds
world = bpy.data.worlds.new("w")
world.use_nodes = True
wn = world.node_tree
bg = wn.nodes["Background"]
tc = wn.nodes.new("ShaderNodeTexCoord")
sep = wn.nodes.new("ShaderNodeSeparateXYZ")
ramp = wn.nodes.new("ShaderNodeValToRGB")
cr = ramp.color_ramp
cr.elements[0].position, cr.elements[0].color = 0.0, hexc("#ffb347")
cr.elements[1].position, cr.elements[1].color = 0.55, hexc("#2a1f63")
for pos, col in ((0.06, "#ff7a3c"), (0.16, "#ff4f6e"), (0.32, "#8a3a9a")):
    e = cr.elements.new(pos); e.color = hexc(col)
wn.links.new(tc.outputs["Generated"], sep.inputs[0])
wn.links.new(sep.outputs["Z"], ramp.inputs[0])
wn.links.new(ramp.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.0
sc.world = world


def emissive(name, col, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexc(col)
    b.inputs["Emission Color"].default_value = hexc(col)
    b.inputs["Emission Strength"].default_value = strength
    return m


SUNDIR = (-30, 90, 9)   # square Minecraft sun low over the horizon, behind the character
sun = box("sunsq", -4, 4, -.1, .1, -4, 4, mats=same(emissive("sunm", "#fff1b0", 12)), loc=SUNDIR)
glow = box("sunglow", -6, 6, .2, .3, -6, 6, mats=same(emissive("glowm", "#ffb050", 2.0)), loc=SUNDIR)
cm = emissive("cloud", "#ffc2b8", 0.9)
for k in range(9):
    cx, cy, cz = rng.uniform(-80, 90), rng.uniform(80, 140), rng.uniform(28, 55)
    w, d = rng.uniform(6, 16), rng.uniform(3, 7)
    box(f"cloud{k}", cx - w, cx + w, cy - d, cy + d, cz, cz + 0.8, mats=same(cm))

key = bpy.data.lights.new("sun", "SUN")
key.energy = 4.5
key.color = (1.0, 0.62, 0.32)
key.angle = math.radians(2)
ko = bpy.data.objects.new("sun", key)
ko.rotation_euler = (math.radians(80), 0, math.radians(165))   # low, from behind -> rim light
sc.collection.objects.link(ko)
fill_l = bpy.data.lights.new("fill", "AREA")
fill_l.energy = 450; fill_l.size = 4; fill_l.color = (1.0, 0.78, 0.62)
fo = bpy.data.objects.new("fill", fill_l)
fo.location = (-3.0, -4.0, 4.0)
sc.collection.objects.link(fo)
c = fo.constraints.new("TRACK_TO"); c.target = rig
pink_l = bpy.data.lights.new("pinkrim", "AREA")
pink_l.energy = 300; pink_l.size = 3; pink_l.color = (1.0, 0.35, 0.7)
po = bpy.data.objects.new("pinkrim", pink_l)
po.location = (4.5, -1.0, 2.5)
sc.collection.objects.link(po)
c = po.constraints.new("TRACK_TO"); c.target = rig

# ---------------------------------------------------------------- camera
target = bpy.data.objects.new("target", None)
sc.collection.objects.link(target)
target.location = (-0.75, 2.0, 2.5)
cam_d = bpy.data.cameras.new("cam")
cam_d.lens = 26
cam = bpy.data.objects.new("cam", cam_d)
sc.collection.objects.link(cam)
cam.location = (-1.1, -3.5, 1.0)
c = cam.constraints.new("TRACK_TO"); c.target = target
sc.camera = cam

if HERO:
    rig.rotation_euler = [math.radians(a) for a in (0, 0, -18)]
    head.rotation_euler = [math.radians(a) for a in (4, 0, -6)]
    arm_l.rotation_euler = [math.radians(a) for a in (-30, 0, 28)]
    eye = emissive("eyeglow", "#22d8ff", 4)
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    for ex in (-3, 2):   # iris pixels x=1..2 and x=5..6 on row 5 of the face
        box("eye", ex * P, (ex + 2) * P, -4.04 * P, -4.0 * P, 1 * P, 3 * P, mats=same(eye), parent=head)
    # V3 expressive face: angry slanted brows + open battle-shout mouth with teeth
    brow = emissive("brow", "#0a0508", 0)
    for sx, ang in ((-2.1, 22), (2.1, -22)):
        bo = box("brow", -1.7 * P, 1.7 * P, -0.35 * P, 0.35 * P, -0.45 * P, 0.45 * P, mats=same(brow), parent=head,
                 loc=(sx * P, -4.2 * P, 4.1 * P))
        bo.rotation_euler = (0, math.radians(ang), 0)
    mouth = emissive("mouth", "#3d0611", 0)
    box("mouth", -2 * P, 2 * P, -4.1 * P, -4.0 * P, 0.1 * P, 1.2 * P, mats=same(mouth), parent=head)
    teeth = emissive("teeth", "#f4f0ea", 0.3)
    box("teeth", -1.7 * P, 1.7 * P, -4.14 * P, -4.1 * P, 0.85 * P, 1.2 * P, mats=same(teeth), parent=head)
    for nm in ("rimL", "rimR"):
        pass
    # sunset relight: hot orange rim from behind-left, cyan water bounce from below, soft warm key
    key.energy = 1.7
    key.color = (1.0, 0.85, 0.7)
    ko.rotation_euler = (math.radians(55), 0, math.radians(-50))   # warm key from camera-left
    fill_l.energy = 25
    bg.inputs["Strength"].default_value = 0.18
    pink_l.energy = 0
    for nm, loc, en, col, sz in (("rimL", (-2.5, 2.5, 2.6), 2600, (1.0, 0.55, 0.2), 2.5),
                                 ("rimR", (2.8, 2.0, 2.2), 1800, (1.0, 0.45, 0.6), 2.5),
                                 ("bounce", (0.2, -2.2, -0.6), 140, (0.3, 0.95, 1.0), 4)):
        ld = bpy.data.lights.new(nm, "AREA"); ld.energy = en; ld.color = col; ld.size = sz
        lo = bpy.data.objects.new(nm, ld); lo.location = Vector(loc) + rig.location
        sc.collection.objects.link(lo)
        cc = lo.constraints.new("TRACK_TO"); cc.target = rig
if CHAR:
  if not HERO:
    # dive pose
      rig.rotation_euler = [math.radians(a) for a in (200, 35, 180)]
      head.rotation_euler = [math.radians(a) for a in (-35, 0, 0)]
      arm_r.rotation_euler = [math.radians(a) for a in (-175, -12, 0)]
      arm_l.rotation_euler = [math.radians(a) for a in (-165, 18, 0)]
      leg_r.rotation_euler = [math.radians(a) for a in (12, 0, -6)]
      leg_l.rotation_euler = [math.radians(a) for a in (-20, 0, 6)]
  if True:
    keep = {rig, sword} | set(rig.children_recursive) | set(sword.children_recursive)
    for o in sc.objects:
        if o.type == "MESH" and o not in keep:
            o.hide_render = True
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = 2000
    for c in list(cam.constraints):
        cam.constraints.remove(c)
    cam.location = rig.location + Vector((0.6, -6.0, 0.2))
    aim = bpy.data.objects.new("aim", None); sc.collection.objects.link(aim)
    aim.location = rig.location + Vector((0.15, 0, -0.75))
    tc_ = cam.constraints.new("TRACK_TO"); tc_.target = aim
    cam_d.lens = 42
    if HERO:
        cam.location = rig.location + Vector((-0.5, -3.6, 0.55))
        aim.location = rig.location + Vector((-0.2, 0, 0.95))
        cam_d.lens = 32
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)
