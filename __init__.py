bl_info = {
    "name": " My Pie Menus",
    "description": "Collection of custom pie menus for me baybey",
    "author": "Jake Mobley",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "category": "",
}


if "bpy" in locals():
    import importlib

    importlib.reload(mesh_add_pie)
    importlib.reload(other_objects_pie)
    importlib.reload(utils)
    importlib.reload(add_modifier)
    importlib.reload(custom_modifier_operators)

else:
    import bpy
    from my_pie_menus import custom_modifier_operators
    from my_pie_menus import mesh_add_pie
    from my_pie_menus import other_objects_pie
    from my_pie_menus import add_modifier
    from my_pie_menus import utils


def create_keymap(
    name: str,
    letter: str,
    class_name: str,
    shift=False,
    ctrl=False,
    alt=False,
):

    wm = bpy.context.window_manager
    default_kms = wm.keyconfigs.default.keymaps
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name=name)
        kmi = km.keymap_items.new("wm.call_menu_pie", letter, "PRESS", shift=shift, ctrl=ctrl, alt=alt)
        kmi.properties.name = class_name
        addon_keymaps.append((km, kmi))
        kmi_string = kmi.to_string()
    for keymap in default_kms[name].keymap_items:
        dkm_string = keymap.to_string()
        if kmi_string == dkm_string:
            keymap.active = False


addon_keymaps = []


classes = (
    # make sure dependency classes go first
    utils.AddCameraCustom,
    utils.AddLatticeCustom,
    utils.AddMannequin,
    custom_modifier_operators.CustomAddMirrorModifier,
    custom_modifier_operators.CustomAddBevelModifier,
    custom_modifier_operators.CustomAddQuickBevSubSurfModifier,
    custom_modifier_operators.CustomSimpleDeform,
    custom_modifier_operators.CustomShrinkwrap,
    custom_modifier_operators.CustomLattice,
    custom_modifier_operators.CustomRemesh,
    custom_modifier_operators.CustomDecimate,
    add_modifier.PIE_MT_AddModifier,
    mesh_add_pie.PIE_MT_AddMesh,
    other_objects_pie.PIE_MT_AddOtherObjects,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

        create_keymap(
            "Object Mode",
            "A",
            "PIE_MT_AddMesh",
            shift=True,
        )
        create_keymap(
            "Object Mode",
            "A",
            "PIE_MT_AddOtherObjects",
            shift=True,
            ctrl=True,
        )
        create_keymap(
            "Object Mode",
            "Q",
            "PIE_MT_AddModifier",
            shift=True,
            alt=True,
        )


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
