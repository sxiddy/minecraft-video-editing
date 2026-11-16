"""Blender: Critical SMP survival thumbnail - hero + survival props + lurking creeper, one lit scene.

blender -b -P scene_crit.py -- <abs_out.png> [percent] [samples]
Renders RGBA (film transparent) with a shadow catcher; compose_crit.py lays it over the 4K plate.
"""
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else os.path.join(HERE, "assets", "scene_crit.png")
PCT = int(argv[1]) if len(argv) > 1 else 100
SAMPLES = int(argv[2]) if len(argv) > 2 else 192

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
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.resolution_percentage = PCT
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"
sc.render.film_transparent = True
sc.view_settings.view_transform = "Standard"   # AgX washed reds to pink (LESSONS thumb-v2)
sc.view_settings.look = "None"
P = 1 / 16.0


def hexc(h, a=1.0):
    h = h.lstrip("#")
    s = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return (*[v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in s], a)


def srgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [1.0])


def make_image(name, arr):
    h, w = arr.shape[:2]
    img = bpy.data.images.new(name, w, h, alpha=True)
    img.pixels = np.flipud(arr).ravel().tolist()
    img.pack()
    return img


def pixel_material(name, img, rough=0.7, alpha=False, emit=None, emit_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img
    t.interpolation = "Closest"
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    if alpha:
        nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = rough
    if emit is not None:
        e = nt.nodes.new("ShaderNodeTexImage")
        e.image = emit
        e.interpolation = "Closest"
        nt.links.new(e.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit_strength
    return m


def flat(name, col, rough=0.5, emit=0.0, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexc(col)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = hexc(col)
        b.inputs["Emission Strength"].default_value = emit
    return m


def regions(u, v, w, h, d):
    return {"top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d),
            "right": (u, v + d, d, h), "front": (u + d, v + d, w, h),
            "left": (u + d + w, v + d, d, h), "back": (u + 2 * d + w, v + d, w, h)}


def same(m):
    return {k: m for k in ("front", "back", "left", "right", "top", "bottom")}


def box(name, x0, x1, y0, y1, z0, z1, uvs=None, mats=None, parent=None, loc=(0, 0, 0), tex=(64, 64)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    V = {}
    for x in (x0, x1):
        for y in (y0, y1):
            for z in (z0, z1):
                V[(x, y, z)] = bm.verts.new((x, y, z))
    faces = {
        "front": [(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)],
        "back": [(x1, y1, z1), (x0, y1, z1), (x0, y1, z0), (x1, y1, z0)],
        "right": [(x0, y1, z1), (x0, y0, z1), (x0, y0, z0), (x0, y1, z0)],
        "left": [(x1, y0, z1), (x1, y1, z1), (x1, y1, z0), (x1, y0, z0)],
        "top": [(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)],
        "bottom": [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)],
    }
    uvl = bm.loops.layers.uv.new()
    mat_list = []
    TW, TH = tex
    for fname, cs in faces.items():
        fa = bm.faces.new([V[c] for c in cs])
        if mats:
            m = mats[fname]
            if m not in mat_list:
                mat_list.append(m)
            fa.material_index = mat_list.index(m)
        if uvs:
            u, v, w, h = uvs[fname]
            uvc = [(u / TW, 1 - v / TH), ((u + w) / TW, 1 - v / TH),
                   ((u + w) / TW, 1 - (v + h) / TH), (u / TW, 1 - (v + h) / TH)]
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


def part(name, mat, uv_origin, w, h, d, offs, pivot, parent, rot, inflate=0.0, tex=(64, 64)):
    x0, y0, z0 = offs
    e = inflate
    o = box(name, (x0 - e) * P, (x0 + w + e) * P, (y0 - e) * P, (y0 + d + e) * P,
            (z0 - e) * P, (z0 + h + e) * P, uvs=regions(*uv_origin, w, h, d),
            mats=same(mat), parent=parent, loc=[c * P for c in pivot], tex=tex)
    o.rotation_euler = [math.radians(a) for a in rot]
    if inflate == 0.0:
        bv = o.modifiers.new("bevel", "BEVEL"); bv.width = 0.22 * P; bv.segments = 2
        o.modifiers.new("wn", "WEIGHTED_NORMAL")
    return o


def voxel_sprite(name, grid, palette, unit, parent=None, emit_keys=(), emit_strength=0.0):
    """grid: list of strings, row 0 = top; builds along local X (cols) and Z (rows); grip at origin."""
    root = bpy.data.objects.new(name, None)
    sc.collection.objects.link(root)
    if parent:
        root.parent = parent
    mats = {}
    rows = len(grid)
    for y, line in enumerate(grid):
        for x, ch in enumerate(line):
            if ch == ".":
                continue
            if ch not in mats:
                mats[ch] = flat(f"{name}_{ch}", palette[ch], 0.35 if ch in "wW" else 0.6,
                                emit_strength if ch in emit_keys else 0.0, 0.6 if ch in "wW" else 0.0)
            gz = rows - 1 - y
            box(f"{name}_v", x * unit, (x + 1) * unit, -unit / 2, unit / 2, gz * unit, (gz + 1) * unit,
                mats=same(mats[ch]), parent=root)
    return root


# ---------------------------------------------------------------- materials
skin_img = bpy.data.images.load(os.path.join(HERE, "assets", "skin_crit.png")); skin_img.pack()
skin = pixel_material("skin", skin_img, 0.65, alpha=True)
cape_img = bpy.data.images.load(os.path.join(HERE, "assets", "cape_crit.png")); cape_img.pack()
cape_m = pixel_material("cape", cape_img, 0.8)


def noisy(arr, amt=0.08, seed=1):
    r = np.random.default_rng(seed)
    out = arr.copy()
    out[..., :3] = np.clip(arr[..., :3] * (1 + r.uniform(-amt, amt, arr.shape[:2]))[..., None], 0, 1)
    return out


def tex16(fn, seed):
    a = np.zeros((16, 16, 4))
    for y in range(16):
        for x in range(16):
            a[y, x] = fn(x, y)
    return noisy(a, 0.09, seed)


def plank(x, y):
    if y % 4 == 3:
        return srgb("#6e5130")
    return srgb("#b08a52") if (x * 7 + y) % 5 else srgb("#9d7745")


def table_top(x, y):
    if x in (0, 15) or y in (0, 15):
        return srgb("#5d3e22")
    if x in (5, 10) or y in (5, 10):
        return srgb("#4a2f18")
    return srgb("#9c6c3c") if (x + y) % 3 else srgb("#86592f")


def table_side(x, y):
    if y < 3:
        return srgb("#5d3e22") if y == 2 else srgb("#9c6c3c")
    if 3 <= x <= 5 and 5 <= y <= 13:
        return srgb("#9a9aa0") if y < 8 else srgb("#6d4a2a")
    if 9 <= x <= 12 and 5 <= y <= 7:
        return srgb("#b0b0b6")
    if 10 <= x <= 11 and 8 <= y <= 13:
        return srgb("#6d4a2a")
    return plank(x, y)


def stone(x, y):
    v = (x * 13 + y * 7 + (x * y) % 5) % 6
    return srgb(["#8a8a8a", "#7b7b7b", "#969696", "#6e6e6e", "#858585", "#909090"][v])


def furnace_front(x, y):
    if 3 <= x <= 12 and 9 <= y <= 13:
        return srgb("#ffb028") if y > 11 else (srgb("#ff6a10") if (x + y) % 2 else srgb("#ffd25a"))
    if 3 <= x <= 12 and 8 == y:
        return srgb("#2a2a2a")
    if 3 <= x <= 12 and 2 <= y <= 5:
        return srgb("#3a3a3a")
    return stone(x, y)


def furnace_emit(x, y):
    if 3 <= x <= 12 and 9 <= y <= 13:
        return furnace_front(x, y)
    return np.array([0, 0, 0, 1.0])


def grass_top(x, y):
    return srgb(["#7a8f3a", "#6f8434", "#879c42", "#5f7430"][(x * 5 + y * 3 + (x * y) % 3) % 4])


def grass_side(x, y):
    if y < 3 or (y == 3 and (x * 7) % 3 == 0):
        return grass_top(x, y)
    return srgb(["#7a5536", "#6b4a2f", "#8a6340", "#5e4029"][(x * 3 + y * 5 + (x * y) % 4) % 4])


IMG = {k: make_image(k, tex16(fn, i)) for i, (k, fn) in enumerate([
    ("ttop", table_top), ("tside", table_side), ("stone", stone), ("plank", plank),
    ("ffront", furnace_front), ("femit", furnace_emit), ("gtop", grass_top), ("gside", grass_side)])}
MAT = {k: pixel_material(k, IMG[k], 0.8) for k in ("ttop", "tside", "stone", "plank", "gtop", "gside")}
MAT["ffront"] = pixel_material("ffront", IMG["ffront"], 0.8, emit=IMG["femit"], emit_strength=4)


def block(name, loc, mats, rotz=0.0):
    o = box(name, -.5, .5, -.5, .5, -.5, .5, mats=mats, loc=loc)
    o.rotation_euler[2] = math.radians(rotz)
    bv = o.modifiers.new("bevel", "BEVEL"); bv.width = 0.012; bv.segments = 2
    return o


# ---------------------------------------------------------------- hero (Critical SMP player)
rig = bpy.data.objects.new("rig", None)
sc.collection.objects.link(rig)
rig.location = (0.0, 0.0, 12 * P)
rig.rotation_euler = (0, 0, math.radians(-22))     # turned slightly toward the logo side
body = part("body", skin, (16, 16), 8, 12, 4, (-4, -2, 0), (0, 0, 0), rig, (0, 0, 0))
head = part("head", skin, (0, 0), 8, 8, 8, (-4, -4, 0), (0, 0, 12), rig, (-6, 0, 10))
arm_r = part("arm_r", skin, (40, 16), 4, 12, 4, (-2, -2, -10), (-6, 0, 10), rig, (-38, 0, -22))   # torch arm (viewer left)
arm_l = part("arm_l", skin, (32, 48), 4, 12, 4, (-2, -2, -10), (6, 0, 10), rig, (-76, 0, 26))    # sword arm forward
leg_r = part("leg_r", skin, (0, 16), 4, 12, 4, (-2, -2, -12), (-2, 0, 0), rig, (8, 0, -4))
leg_l = part("leg_l", skin, (16, 48), 4, 12, 4, (-2, -2, -12), (2, 0, 0), rig, (-10, 0, 5))
part("head_ov", skin, (32, 0), 8, 8, 8, (-4, -4, 0), (0, 0, 0), head, (0, 0, 0), inflate=0.5)
part("body_ov", skin, (16, 32), 8, 12, 4, (-4, -2, 0), (0, 0, 0), body, (0, 0, 0), inflate=0.25)
part("arm_r_ov", skin, (40, 32), 4, 12, 4, (-2, -2, -10), (0, 0, 0), arm_r, (0, 0, 0), inflate=0.25)
part("arm_l_ov", skin, (48, 48), 4, 12, 4, (-2, -2, -10), (0, 0, 0), arm_l, (0, 0, 0), inflate=0.25)
# cape: 10x16x1 hanging from the shoulders, swung back a little
cape_piv = bpy.data.objects.new("cape_piv", None); sc.collection.objects.link(cape_piv)
cape_piv.parent = body; cape_piv.location = (0, 2.2 * P, 12 * P); cape_piv.rotation_euler = (math.radians(14), 0, 0)
part("cape", cape_m, (0, 0), 10, 16, 1, (-5, 0, -16), (0, 0, 0), cape_piv, (0, 0, 0), tex=(64, 32))

# face: determined brows (3D boxes so they survive 320 px) + glowing red eyes
brow = flat("brow", "#120609", 0.6)
for sx, ang in ((-2.1, 20), (2.1, -20)):
    bo = box("brow", -1.6 * P, 1.6 * P, -0.35 * P, 0.35 * P, -0.4 * P, 0.4 * P, mats=same(brow), parent=head,
             loc=(sx * P, -4.55 * P, 4.75 * P))
    bo.rotation_euler = (0, math.radians(ang), 0)
eye = flat("eyeglow", "#ff1020", 0.4, emit=2.2)
for ex in (-2, 1):
    box("eye", ex * P, (ex + 1) * P, -4.53 * P, -4.5 * P, 2.0 * P, 4.0 * P,
        mats=same(eye), parent=head)

mouth = flat("mouth", "#3d0611", 0.6)
box("mouth", -1.5 * P, 1.5 * P, -4.56 * P, -4.5 * P, -0.2 * P, 1.6 * P, mats=same(mouth), parent=head)
teeth = flat("teeth", "#f4f0ea", 0.5)
box("teeth", -1.3 * P, 1.3 * P, -4.6 * P, -4.56 * P, 1.2 * P, 1.55 * P, mats=same(teeth), parent=head)
box("teeth2", -1.0 * P, 1.0 * P, -4.6 * P, -4.56 * P, -0.15 * P, 0.15 * P, mats=same(teeth), parent=head)

# ---------------------------------------------------------------- held items (built in world space at the hands)
bpy.context.view_layer.update()


def hand(arm):
    return arm.matrix_world @ Vector((0, 0, -10.5 * P))


SWORD = [
    "..e.",
    ".eWw",
    ".eWw",
    ".eWw",
    ".eWw",
    ".eWw",
    ".eWw",
    ".eWw",
    ".eWw",
    ".eWw",
    ".eWw",
    "gggggg"[:4],
    "..h.",
    "..h.",
    "..h.",
]
sword = voxel_sprite("sword", SWORD, {"w": "#aab3c2", "W": "#e9eef5", "e": "#5d6676", "g": "#2f2c38", "h": "#5a3a1e"}, 1.0 * P)
for o in sword.children:
    o.location.x -= 2.5 * 1.0 * P
sword.location = hand(arm_l)
sw_dir = Vector((-0.12, -0.72, 0.68)).normalized()
sword.rotation_euler = sw_dir.to_track_quat("Z", "Y").to_euler()
sword.location -= sw_dir * 3.2 * 1.0 * P
# blade glint light
TORCH = ["ff", "Ff", "ss", "ss", "ss", "ss", "ss", "ss", "ss"]
torch = voxel_sprite("torch", TORCH, {"f": "#ffcf3a", "F": "#fff2a0", "s": "#6b4a26"}, 1.3 * P,
                     emit_keys=("f", "F"), emit_strength=40)
torch.scale = (0.7, 0.7, 0.7)
th = hand(arm_r)
torch.location = th + Vector((-0.02, -0.04, -0.12))
torch.rotation_euler = (math.radians(-8), math.radians(-10), 0)
tl = bpy.data.lights.new("torchlight", "POINT"); tl.energy = 140; tl.color = (1.0, 0.55, 0.18); tl.shadow_soft_size = 0.08
tlo = bpy.data.objects.new("torchlight", tl); sc.collection.objects.link(tlo)
tlo.location = th + Vector((0.0, -0.18, 0.1))

# ---------------------------------------------------------------- survival props (left of the hero, slightly behind)
tm = {k: MAT["tside"] for k in ("front", "back", "left", "right")}; tm.update(top=MAT["ttop"], bottom=MAT["plank"])
block("crafting", (-2.95, 5.6, 0.5), tm, rotz=20)
fm = {k: MAT["stone"] for k in ("back", "left", "right", "top", "bottom")}; fm["front"] = MAT["ffront"]
block("furnace", (-4.05, 6.1, 0.5), fm, rotz=28)
gm = {k: MAT["gside"] for k in ("front", "back", "left", "right")}; gm.update(top=MAT["gtop"], bottom=MAT["gside"])
fl = bpy.data.lights.new("furnace", "POINT"); fl.energy = 14; fl.color = (1.0, 0.45, 0.12); fl.shadow_soft_size = 0.2
flo = bpy.data.objects.new("furnace", fl); sc.collection.objects.link(flo); flo.location = (-3.75, 5.3, 0.35)

# ---------------------------------------------------------------- creeper sneaking up behind (survival threat)
CR = np.zeros((64, 64, 4))
rngc = np.random.default_rng(3)
greens = [srgb(h) for h in ("#3f8a2a", "#33751f", "#4f9c36", "#2a6418", "#6bb04a", "#1f4f12")]
for y in range(64):
    for x in range(64):
        CR[y, x] = greens[min(5, int(abs(rngc.normal(0, 1.6))))]
fr = regions(0, 0, 8, 8, 8)["front"]
for (x, y) in [(1, 2), (2, 2), (1, 3), (2, 3), (5, 2), (6, 2), (5, 3), (6, 3), (3, 4), (4, 4), (2, 5), (3, 5), (4, 5),
               (5, 5), (2, 6), (5, 6), (3, 6), (4, 6), (2, 7), (5, 7)]:
    CR[fr[1] + y, fr[0] + x] = srgb("#0b0f0a")
creeper_m = pixel_material("creeper", make_image("creeper", CR), 0.75)
cr = bpy.data.objects.new("creeper", None); sc.collection.objects.link(cr)
cr.location = (-1.1, 2.3, 6 * P)
cr.rotation_euler = (0, 0, math.radians(-12))
part("cr_body", creeper_m, (16, 16), 8, 12, 4, (-4, -2, 0), (0, 0, 0), cr, (0, 0, 0))
crh = part("cr_head", creeper_m, (0, 0), 8, 8, 8, (-4, -4, 0), (0, 0, 12), cr, (-4, 0, 8))
for i, (lx, ly) in enumerate(((-2, -4), (2, -4), (-2, 4), (2, 4))):
    part(f"cr_leg{i}", creeper_m, (0, 16), 4, 6, 4, (-2, -2, -6), (lx, ly / 2, 0), cr, (0, 0, 0))

# ---------------------------------------------------------------- ground: shadow catcher
gp = bpy.data.meshes.new("ground")
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=30); bm.to_mesh(gp); bm.free()
ground = bpy.data.objects.new("ground", gp); sc.collection.objects.link(ground)
ground.is_shadow_catcher = True

# ---------------------------------------------------------------- lighting matched to the plate
world = bpy.data.worlds.new("w"); world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = hexc("#5a4a7a")
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.26
sc.world = world
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.2; sun.color = (1.0, 0.68, 0.38); sun.angle = math.radians(3)
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so)
so.rotation_euler = (math.radians(-72), 0, math.radians(-25))   # low sun from behind-right (plate rays)


def area(name, loc, energy, col, size, target):
    ld = bpy.data.lights.new(name, "AREA"); ld.energy = energy; ld.color = col; ld.size = size
    lo = bpy.data.objects.new(name, ld); lo.location = loc; sc.collection.objects.link(lo)
    c = lo.constraints.new("TRACK_TO"); c.target = target
    return lo


aim_hero = bpy.data.objects.new("aim_hero", None); sc.collection.objects.link(aim_hero); aim_hero.location = (0, 0, 1.4)
area("rim_warm", (1.8, 2.6, 2.4), 900, (1.0, 0.6, 0.28), 1.5, aim_hero)       # sun rim, right edge
area("rim_back", (-1.6, 2.4, 2.6), 650, (1.0, 0.5, 0.25), 1.5, aim_hero)      # sun rim, left edge
area("fill_dusk", (-2.8, -3.0, 2.2), 160, (0.55, 0.5, 1.0), 4.0, aim_hero)    # cool dusk fill on the face side
area("cr_rim", (0.6, 4.5, 2.2), 260, (1.0, 0.55, 0.3), 1.2, cr)

# ---------------------------------------------------------------- camera: hero on the right third, low heroic angle
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 33
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam)
cam.location = (-1.0, -3.35, 0.95)
cam.rotation_euler = (math.radians(96.5), 0, math.radians(-4))
sc.camera = cam
cam_d.dof.use_dof = True
cam_d.dof.focus_object = aim_hero
cam_d.dof.aperture_fstop = 2.8

sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)
