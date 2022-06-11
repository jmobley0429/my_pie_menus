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
    importlib.reload(node_editor_operators)

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
    from my_pie_menus.operators import node_editor_operators

    from my_pie_menus.pies import add_pies
    from my_pie_menus.pies import edit_mode_pies
    from my_pie_menus.pies import object_mode_pies


KMS = keymap_settings.KEYMAP_SETTINGS


addon_keymaps = []
modules = [
    modifier_operators,
    add_mesh_operators,
    edit_mode_operators,
    object_mode_operators,
    node_editor_operators,
    add_pies,
    edit_mode_pies,
    object_mode_pies,
]

classes = [cls for module in modules for cls in module.classes]
classes.sort(key=lambda cls: cls.bl_idname)


def register():
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
        bpy.utils.register_class(cls)

    for setting in KMS:
        name, letter, class_name, shift, ctrl, alt, space_type = list(setting.values())
        wm = bpy.context.window_manager
        default_kms = wm.keyconfigs.default.keymaps
        wm = bpy.context.window_manager
        if wm.keyconfigs.addon:
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
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
