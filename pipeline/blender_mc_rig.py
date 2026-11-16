"""Section 8 T2: spawn a real MCprep player rig with a real skin and save it as a .blend.
Runs INSIDE Blender (tested headless on Blender 5.2 + MCprep 3.6.3):

    "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --python pipeline/blender_mc_rig.py -- <skin.png> <out.blend> [slim|classic] [simple]

Get the skin first with mc_skin.py; its .json says slim or classic. "simple" picks the lighter
Simple rig instead of FancyFeet. Prints RESULT lines; the last one is "RESULT OK <file>" on success.
"""
import sys
import traceback

import bpy

def log(*a):
    print("RESULT", *a, flush=True)

def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) < 2:
        log("STOP usage: -- <skin.png> <out.blend> [slim|classic] [simple]")
        return 1
    skin, out = args[0], args[1]
    slim, simple = "slim" in args[2:], "simple" in args[2:]
    if not hasattr(bpy.ops, "mcprep") or not hasattr(bpy.context.scene, "mcprep_props"):
        log("STOP MCprep is not enabled; run setup/install_mcprep.py (setup/INSTALL.md section 4)")
        return 1
    bpy.ops.wm.read_homefile(use_empty=True)
    bpy.ops.mcprep.reload_mobs()
    props = bpy.context.scene.mcprep_props
    mobs = list(getattr(props, "mob_list_all", None) or props.mob_list)
    want = ("Simple Player" if simple else "Player") + (" Slim" if slim else "")
    pick = next((m for m in mobs if m.name == want), None)
    if pick is None:
        log("STOP rig not found:", want, "available:", [m.name for m in mobs if "player" in m.name.lower()])
        return 1
    before = set(bpy.data.objects.keys())
    bpy.ops.mcprep.mob_spawner(mcmob_type=pick.mcmob_type, toLink=False, clearPose=True, prep_materials=False)
    new = [o for o in bpy.data.objects if o.name not in before]
    in_layer = set(bpy.context.view_layer.objects)
    meshes = [o for o in new if o.type == "MESH" and o in in_layer and o.material_slots]
    arms = [o.name for o in new if o.type == "ARMATURE"]
    if not meshes or not arms:
        log("STOP the rig did not spawn (", len(new), "new objects )")
        return 1
    for o in in_layer:
        o.select_set(o in meshes)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.mcprep.applyskin(filepath=skin, new_material=False)
    images = sorted({n.image.filepath for o in meshes for s in o.material_slots
                     if s.material and s.material.node_tree
                     for n in s.material.node_tree.nodes if n.type == "TEX_IMAGE" and n.image})
    if not any(bpy.path.abspath(i).replace("\\", "/").lower() == skin.replace("\\", "/").lower() for i in images):
        log("STOP the skin was not applied; textures on the rig:", images)
        return 1
    bpy.ops.wm.save_as_mainfile(filepath=out)
    log("rig", pick.name, "armatures", arms, "skin", skin)
    log("OK", out)
    return 0

try:
    code = main()
except Exception:
    log("EXCEPTION", traceback.format_exc()[-1200:])
    code = 1
sys.exit(code)
