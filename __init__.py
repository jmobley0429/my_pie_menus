bl_info = {
    "name": " My Pie Menus",
    "description": "Collection of custom pie menus for me baybey",
    "author": "Jake Mobley",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "category": "",
}


def db_block(area: str):
    print(f"{area}\n" * 3)


db_block("**** MY_PIE_MENUS ****")

if "bpy" in locals():
    import importlib

    importlib.reload(custom_operator)
    importlib.reload(modifier_operators)
    importlib.reload(add_mesh_operators)
    importlib.reload(edit_mode_operators)
    importlib.reload(object_mode_operators)
    importlib.reload(node_editor_operators)
    importlib.reload(sculpt_mode_operators)

    importlib.reload(add_pies)
    importlib.reload(edit_mode_pies)
    importlib.reload(object_mode_pies)

else:
    import bpy
    from my_pie_menus.resources import utils

    from my_pie_menus.operators import custom_operator
    from my_pie_menus.operators import modifier_operators
    from my_pie_menus.operators import add_mesh_operators
    from my_pie_menus.operators import edit_mode_operators
    from my_pie_menus.operators import object_mode_operators
    from my_pie_menus.operators import node_editor_operators
    from my_pie_menus.operators import sculpt_mode_operators

    from my_pie_menus.pies import add_pies
    from my_pie_menus.pies import edit_mode_pies
    from my_pie_menus.pies import object_mode_pies
    from my_pie_menus.conf.keymap_settings import KEYMAP_SETTINGS as KMS


modules = [
    modifier_operators,
    add_mesh_operators,
    edit_mode_operators,
    object_mode_operators,
    node_editor_operators,
    add_pies,
    edit_mode_pies,
    object_mode_pies,
    sculpt_mode_operators,
]

classes = [cls for module in modules for cls in module.classes]
classes.sort(key=lambda cls: cls.bl_idname)

addon_keymaps = []


def register_keymap(setting):
    args = list(dict(sorted(setting.items())).values())
    alt, idname, ctrl, letter, name, region_type, shift, space_type = args
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = kc.keymaps.new(name=name, space_type=space_type, region_type=region_type)
    kmi = km.keymap_items.new('wm.call_menu_pie', letter, 'PRESS', shift=shift, ctrl=ctrl, alt=alt)
    kmi.properties.name = idname
    kmi.active = True
    addon_keymaps.append((km, kmi))


def unregister_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
            kc.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
        bpy.utils.register_class(cls)


def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":

    register()
    for setting in KMS:
        register_keymap(setting)
db_block("**** MY_PIE_MENUS ****")
