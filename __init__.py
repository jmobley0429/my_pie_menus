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

    importlib.reload(custom_operator)
    importlib.reload(modifier_operators)
    importlib.reload(add_mesh_operators)
    importlib.reload(edit_mode_operators)
    importlib.reload(object_mode_operators)

    importlib.reload(add_pies)
    importlib.reload(edit_mode_pies)
    importlib.reload(object_mode_pies)

else:
    import bpy
    from my_pie_menus.resources import utils
    from my_pie_menus.conf import keymap_settings

    from my_pie_menus.operators import custom_operator
    from my_pie_menus.operators import modifier_operators
    from my_pie_menus.operators import add_mesh_operators
    from my_pie_menus.operators import edit_mode_operators
    from my_pie_menus.operators import object_mode_operators

    from my_pie_menus.pies import add_pies
    from my_pie_menus.pies import edit_mode_pies
    from my_pie_menus.pies import object_mode_pies


KMS = keymap_settings.KEYMAP_SETTINGS

# classes = (
#     # make sure dependency classes go first
#     utils.AddCameraCustom,
#     utils.AddLatticeCustom,
#     utils.AddMannequin,
#     snap_pie.SetSnap,
#     add_mesh_operators.AddCustomMeshOperator,
#     custom_modifier_operators.CustomAddMirrorModifier,
#     custom_modifier_operators.CustomAddBevelModifier,
#     custom_modifier_operators.CustomAddQuickBevSubSurfModifier,
#     custom_modifier_operators.CustomSimpleDeform,
#     custom_modifier_operators.CustomShrinkwrap,
#     custom_modifier_operators.CustomLattice,
#     custom_modifier_operators.CustomRemesh,
#     custom_modifier_operators.CustomDecimate,
#     custom_modifier_operators.ArrayModalOperator,
#     custom_modifier_operators.SolidifyModalOperator,
#     custom_modifier_operators.ScrewModalOperator,
#     edit_mesh_operators.MESH_OT_reduce_cylinder,
#     lighting_setup.AddLightSetup,
#     add_modifier.PIE_MT_ParticleSubPie,
#     add_modifier.PIE_MT_MeshSubPie,
#     add_modifier.PIE_MT_NormalSubPie,
#     add_modifier.PIE_MT_AddModifier,
#     mesh_add_pie.PIE_MT_AddMesh,
#     other_objects_pie.PIE_MT_AddOtherObjects,
#     snap_pie.PIE_MT_SnapOptions,
#     convert_mesh_curve.PIE_MT_ConvertMeshCurve,
# )

addon_keymaps = []
classes = []
modules = [
    # custom_operator,
    modifier_operators,
    add_mesh_operators,
    edit_mode_operators,
    object_mode_operators,
    add_pies,
    edit_mode_pies,
    object_mode_pies,
]
for module in modules:
    for cls in module.classes:
        classes.append(cls)


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except RuntimeError:
            print(cls)
    for setting in KMS:
        name, letter, class_name, shift, ctrl, alt, space_type = list(setting.values())
        wm = bpy.context.window_manager
        default_kms = wm.keyconfigs.default.keymaps
        wm = bpy.context.window_manager
        if wm.keyconfigs.addon:
            # adding space type makes it work ???
            km = wm.keyconfigs.addon.keymaps.new(name=name, space_type=space_type)
            kmi = km.keymap_items.new('wm.call_menu_pie', letter, 'PRESS', alt=alt, shift=shift, ctrl=ctrl)
            kmi_string = kmi.to_string()
            for keymap in default_kms[name].keymap_items:
                dkm_string = keymap.to_string()
                if kmi_string == dkm_string:
                    keymap.active = False

            kmi.properties.name = class_name
            addon_keymaps.append((km, kmi))


def unregister():

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
