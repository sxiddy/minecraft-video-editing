"""Blender: animated 3D "TIDES / SMP" title for the V2 trailer (same look as thumb/title3d.py).

blender -b -P title3d_anim.py   -> C:/Users/Siddharth D/tides-work/title3d/####.png (1920x1080 RGBA, 60 fps, 300 frames)
Each TIDES letter slams in toward camera with an overshoot (staggered 4 frames), SMP rises in after,
then the whole lockup floats gently. The compositor fades it out.
"""
import bpy, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "assets", "fonts", "pixel", "PressStart2P.ttf")  # chunky pixel caps, per the client reference
OUT = "C:/Users/Siddharth D/tides-work/title3d/"
FRAMES = int(os.environ.get("FRAMES", "300"))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.fps = 60
sc.frame_start, sc.frame_end = int(os.environ.get("START", "1")), int(os.environ.get("END", FRAMES))
sc.render.film_transparent = True
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = 0.5
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
font = bpy.data.fonts.load(FONT)

def hexc(h, a=1.0):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, a)

def face_material(name, top, bottom, side, rough=0.22):
    """Glossy vertical gradient on the front face, a darker solid on the extruded sides."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    n, l = nt.nodes, nt.links
    bsdf = n["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rough
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hexc(bottom)
    ramp.color_ramp.elements[1].color = hexc(top)
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[1].position = 0.85
    l.new(sep.outputs["Y"], ramp.inputs[0])
    sepn = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Normal"], sepn.inputs[0])
    front = n.new("ShaderNodeMath"); front.operation = "GREATER_THAN"; front.inputs[1].default_value = 0.6
    l.new(sepn.outputs["Z"], front.inputs[0])
    mix = n.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs[6].default_value = hexc(side)
    l.new(front.outputs[0], mix.inputs[0])
    l.new(ramp.outputs["Color"], mix.inputs[7])
    l.new(mix.outputs[2], bsdf.inputs["Base Color"])
    l.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 0.25
    return m

def flat_material(name, color):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexc(color)
    b.inputs["Roughness"].default_value = 0.9
    b.inputs["Specular IOR Level"].default_value = 0.0
    return m

def glyph(ch, size, mat, outline_mat, extrude, offset):
    """One letter: glossy face + thick navy outline behind it, both parented to an empty at the letter centre."""
    pivot = bpy.data.objects.new("pv_" + ch, None)
    sc.collection.objects.link(pivot)
    # face, dark navy outline, thin gold rim behind it (the reference logo's treatment); pixel glyphs are all
    # right angles, so a mitred offset keeps the blocks crisp
    for layer, (m, off, ext, z) in enumerate([(mat, 0.0, extrude, 0.0), (outline_mat, offset, extrude * 0.7, extrude * 1.15),
                                               (rim, offset * 1.45, extrude * 0.5, extrude * 1.9)]):
        bpy.ops.object.text_add(location=(0, z, 0))
        o = bpy.context.object
        o.data.body = ch
        o.data.font = font
        o.data.size = size
        o.data.align_x = "CENTER"
        o.data.align_y = "CENTER"
        o.data.extrude = ext
        o.data.bevel_depth = 0.006 if layer == 0 else 0.0
        o.data.bevel_resolution = 1
        o.data.offset = off
        o.rotation_euler = (math.radians(90), 0, 0)
        o.data.materials.append(m)
        o.parent = pivot
    return pivot

def width(ch, size):
    bpy.ops.object.text_add()
    o = bpy.context.object
    o.data.body, o.data.font, o.data.size = ch, font, size
    bpy.context.view_layer.update()
    w = o.dimensions.x
    bpy.data.objects.remove(o)
    return w

aqua = face_material("aqua", "#FFFFFF", "#47B8FF", "#0E3F78", rough=0.3)
gold = face_material("gold", "#FFF6C8", "#FFB43A", "#7A4208", rough=0.3)
rim = flat_material("rim", "#E9A74A")
navy = flat_material("navy", "#061A2E")

group = bpy.data.objects.new("lockup", None)
sc.collection.objects.link(group)
group.rotation_euler[1] = math.radians(-4)

def row(word, size, z, mat, ext, off, gap):
    ws = [width(c, size) for c in word]
    total = sum(ws) + gap * (len(word) - 1)
    x = -total / 2
    out = []
    for c, w in zip(word, ws):
        p = glyph(c, size, mat, navy, ext, off)
        p.parent = group
        p.location = (x + w / 2, 0, z)
        x += w + gap
        out.append(p)
    return out

tides = row("TIDES", 0.95, 0.38, aqua, 0.16, 0.07, 0.02)
smp = row("SMP", 0.55, -0.55, gold, 0.11, 0.05, 0.03)

def key(o, f, loc=None, rot=None, scale=None):
    if loc is not None:
        o.location = loc; o.keyframe_insert("location", frame=f)
    if rot is not None:
        o.rotation_euler = [math.radians(a) for a in rot]; o.keyframe_insert("rotation_euler", frame=f)
    if scale is not None:
        o.scale = (scale,) * 3; o.keyframe_insert("scale", frame=f)

# TIDES: each letter flies from toward the camera, tumbling, and slams into place with a squash overshoot.
for i, p in enumerate(tides):
    x, y, z = p.location
    f0 = 2 + i * 4
    key(p, f0, (x * 1.6, -7.0, z + 1.2), (-75, 0, (-1) ** i * 25), 0.6)
    key(p, f0 + 9, (x, 0.25, z), (8, 0, 0), 1.12)
    key(p, f0 + 14, (x, -0.05, z), (-3, 0, 0), 0.96)
    key(p, f0 + 22, (x, 0, z), (0, 0, 0), 1.0)
# SMP rises from below the line and pops.
for i, p in enumerate(smp):
    x, y, z = p.location
    f0 = 30 + i * 3
    key(p, f0, (x, 0, z - 1.4), (0, 0, 0), 0.2)
    key(p, f0 + 10, (x, 0, z + 0.08), (0, 0, 0), 1.1)
    key(p, f0 + 18, (x, 0, z), (0, 0, 0), 1.0)
# whole lockup: slow float and turn for the rest of the hold
key(group, 1, (0, 0, 0), (0, -4, -3))
key(group, FRAMES, (0, 0, 0.06), (0, -4, 4))

for a in bpy.data.actions:
    for fc in getattr(a, "fcurves", []):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.easing = "AUTO"
grp_action = group.animation_data.action if group.animation_data else None
if grp_action:
    for fc in getattr(grp_action, "fcurves", []):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"

cam_data = bpy.data.cameras.new("cam")
cam_data.lens = 82
cam = bpy.data.objects.new("cam", cam_data)
sc.collection.objects.link(cam)
cam.rotation_euler = (math.radians(95), 0, math.radians(2))
sc.camera = cam
cam.location = (0.3, -12.6, -1.0); cam.keyframe_insert("location", frame=1)
cam.location = (0.3, -11.6, -1.0); cam.keyframe_insert("location", frame=FRAMES)

def light(kind, loc, rot, energy, color, size=None):
    d = bpy.data.lights.new(kind + str(len(bpy.data.lights)), kind)
    d.energy = energy
    d.color = color
    if size and kind == "AREA":
        d.size = size
    o = bpy.data.objects.new(d.name, d)
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    sc.collection.objects.link(o)

light("SUN", (0, 0, 0), (55, -25, 20), 3.2, (1.0, 0.93, 0.82))
light("AREA", (-4, -5, 4), (60, 0, -35), 900, (1.0, 0.75, 0.45), 6)
light("AREA", (5, -3, -2), (100, 0, 45), 500, (0.45, 0.85, 1.0), 5)
world = bpy.data.worlds.new("w")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.25, 0.32, 0.38, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
sc.world = world

os.makedirs(OUT, exist_ok=True)
sc.render.filepath = OUT + "####"
bpy.ops.render.render(animation=True)
print("WROTE", OUT)
