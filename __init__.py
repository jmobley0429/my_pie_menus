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
    importlib.reload(weight_paint_operators)
    importlib.reload(uv_operators)
    importlib.reload(add_pies)
    importlib.reload(edit_mode_pies)
    importlib.reload(object_mode_pies)
    importlib.reload(sculpt_mode_pies)
    importlib.reload(uv_pies)
    importlib.reload(weight_paint_pies)
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
    from my_pie_menus.operators import weight_paint_operators

    from my_pie_menus.menus import add_pies
    from my_pie_menus.menus import edit_mode_pies
    from my_pie_menus.menus import object_mode_pies
    from my_pie_menus.menus import sculpt_mode_pies
    from my_pie_menus.menus import uv_pies
    from my_pie_menus.menus import weight_paint_pies

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
    weight_paint_operators,
    uv_pies,
    weight_paint_pies,
]

menu_funcs = [
    (bpy.types.DATA_PT_modifiers, "prepend", modifier_operators.menu_func),
    (bpy.types.VIEW3D_MT_select_object, "append",
     object_mode_operators.deselect_parented_objs_menu_func),
]


global addon_keymaps
addon_keymaps = []


def register():

    for module in modules:
        print(f"registering {module.__name__}")
        module.register()


def unregister():
    for module in modules:

        module.unregister()


if __name__ == "__main__":
    bpy.ops.preferences.addon_enable(module="space_view3d_align_tools")
    bpy.ops.preferences.addon_enable(module="add_mesh_extra_objects")
    bpy.ops.preferences.addon_enable(module="add_curve_extra_objects")
    bpy.ops.preferences.addon_enable(module="mesh_looptools")
    bpy.ops.preferences.addon_enable(module="node_wrangler")
    bpy.ops.preferences.addon_enable(module="io_import_images_as_planes")
    register()
