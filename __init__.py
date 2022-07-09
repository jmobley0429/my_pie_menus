bl_info = {
    "name": " My Pie Menus",
    "description": "Collection of custom pie menus and operators",
    "author": "Jake Mobley",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "category": "",
}


def db_block(area: str):
    print(f"{area}\n" * 3)


db_block("**** my_pie_menus ****")

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


def register():
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
        bpy.utils.register_class(cls)


def unregister():
    utils.unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


db_block("**** my_pie_menus ****")
if __name__ == "__main__":

    register()
    for setting in KMS:
        utils.register_keymap(setting, addon_keymaps)
