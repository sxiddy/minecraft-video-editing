import bpy, sys, addon_utils
zip_path = sys.argv[sys.argv.index("--")+1]
try:
    bpy.ops.preferences.addon_install(filepath=zip_path, overwrite=True)
    print("INSTALL_OK")
except Exception as e:
    print("INSTALL_ERR", e)
names = [m.__name__ for m in addon_utils.modules() if "mcprep" in m.__name__.lower()]
print("FOUND", names)
for n in names:
    try:
        bpy.ops.preferences.addon_enable(module=n)
        print("ENABLED", n, hasattr(bpy.ops, "mcprep"))
    except Exception as e:
        print("ENABLE_ERR", n, e)
bpy.ops.wm.save_userpref()
print("OPS", [o for o in dir(bpy.ops.mcprep)][:40] if hasattr(bpy.ops,"mcprep") else "none")
