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


if "bpy" in locals():
    import importlib

    importlib.reload(custom_operator)
    importlib.reload(modifier_operators)
    importlib.reload(add_mesh_operators)
    importlib.reload(edit_mode_operators)
    importlib.reload(object_mode_operators)
    importlib.reload(node_editor_operators)
    importlib.reload(sculpt_mode_operators)
    importlib.reload(uv_operators)
    importlib.reload(add_pies)
    importlib.reload(edit_mode_pies)
    importlib.reload(object_mode_pies)
    importlib.reload(sculpt_mode_pies)
    importlib.reload(uv_pies)
    importlib.reload(utils)

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
    from my_pie_menus.operators import uv_operators

    from my_pie_menus.menus import add_pies
    from my_pie_menus.menus import edit_mode_pies
    from my_pie_menus.menus import object_mode_pies
    from my_pie_menus.menus import sculpt_mode_pies
    from my_pie_menus.menus import uv_pies
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
    sculpt_mode_pies,
    sculpt_mode_operators,
    uv_operators,
    uv_pies,
]

menu_funcs = [
    (bpy.types.DATA_PT_modifiers, "prepend", modifier_operators.menu_func),
    (bpy.types.VIEW3D_MT_select_object, "append", object_mode_operators.deselect_parented_objs_menu_func),
]

classes = [cls for module in modules for cls in module.classes]
classes.sort(key=lambda cls: cls.bl_idname)

addon_keymaps = []


def register():
    sculpt_mode_pies.create_icons()
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
        bpy.utils.register_class(cls)
        if type(cls) == type(bpy.types.PropertyGroup):
            prop = bpy.props.PointerProperty(type=cls)
            setattr(bpy.types.WindowManager, cls.scene_prop_id, prop)

    for menu, action, func in menu_funcs:
        getattr(menu, "remove")(func)
        getattr(menu, action)(func)


def unregister():
    sculpt_mode_pies.release_icons()
    utils.unregister_keymaps(addon_keymaps)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    for menu, _, func in menu_funcs:
        getattr(menu, "remove")(func)


if __name__ == "__main__":
    db.db_block('*****BEGINNING OF REGISTER*****')
    register()
    for setting in KMS:
        utils.register_keymap(setting, addon_keymaps)

    db.db_block('*****END OF REGISTER*****')
