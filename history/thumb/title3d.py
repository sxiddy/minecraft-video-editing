"""Blender: render the 3D "TIDES / SMP" thumbnail title on a transparent background.

blender -b -P title3d.py   -> assets/title3d.png (1920x1080 RGBA)
"""
import bpy, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "assets", "LuckiestGuy.ttf")
OUT = os.path.join(HERE, "assets", "title3d.png")

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.film_transparent = True
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
    # a touch of emission on the face so the colours stay bright and clean
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

def text(body, size, y, mat, outline_mat, extrude, offset, space=1.0):
    objs = []
    for layer, (m, off, ext, z) in enumerate([(mat, 0.0, extrude, 0.0), (outline_mat, offset, extrude * 0.6, extrude * 1.2)]):
        bpy.ops.object.text_add(location=(0, z, y))
        o = bpy.context.object
        o.data.body = body
        o.data.font = font
        o.data.size = size
        o.data.align_x = "CENTER"
        o.data.align_y = "CENTER"
        o.data.space_character = space
        o.data.extrude = ext
        o.data.bevel_depth = 0.022 if layer == 0 else 0.0
        o.data.bevel_resolution = 4
        o.data.offset = off
        o.rotation_euler = (math.radians(90), 0, 0)
        o.data.materials.append(m)
        objs.append(o)
    return objs

aqua = face_material("aqua", "#F4FFFF", "#28D3F0", "#0B4F7A")
gold = face_material("gold", "#FFF3A6", "#FFA81E", "#8A4A06")
navy = flat_material("navy", "#061A2E")

title = text("TIDES", 1.55, 0.42, aqua, navy, 0.20, 0.11, 1.02)
smp = text("SMP", 0.9, -0.66, gold, navy, 0.14, 0.085, 1.15)
for o in title + smp:  # slight upward tilt reads as energetic, like the reference thumbnails
    o.rotation_euler[1] = math.radians(-4)

cam_data = bpy.data.cameras.new("cam")
cam_data.lens = 82
cam = bpy.data.objects.new("cam", cam_data)
sc.collection.objects.link(cam)
cam.location = (0.3, -11.5, -1.0)
cam.rotation_euler = (math.radians(95), 0, math.radians(2))
sc.camera = cam

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

sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)
