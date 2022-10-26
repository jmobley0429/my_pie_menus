import bpy
from bpy.types import Menu

brush_icons = {}


def create_icons():
    global brush_icons

    icons_directory = bpy.utils.system_resource('DATAFILES', path="icons")
    brushes = [
        "border_mask",
        "border_hide",
        "box_trim",
        "line_project",
    ]
    import os

    for brush in brushes:
        icon_str = f"ops.sculpt.{brush}.dat"
        filename = f"{icons_directory}/{icon_str}"
        icon_value = bpy.app.icons.new_triangles_from_file(filename)
        brush_icons[brush] = icon_value


def release_icons():
    global brush_icons
    for value in brush_icons.values():
        bpy.app.icons.release(value)


class PIE_MT_hide_mask_brushes(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Hide/Mask Brush Menu"
    bl_idname = "PIE_MT_hide_mask_brushes"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        global brush_icons
        layout = self.layout

        pie = layout.menu_pie()
        op = pie.operator("wm.tool_set_by_id", text="   Mask", icon_value=brush_icons["border_mask"])
        op.name = "builtin.box_mask"
        op = pie.operator("wm.tool_set_by_id", text="   Hide", icon_value=brush_icons["border_hide"])
        op.name = "builtin.box_hide"
        op = pie.operator("wm.tool_set_by_id", text="   Trim", icon_value=brush_icons["box_trim"])
        op.name = "builtin.box_trim"
        op = pie.operator("wm.tool_set_by_id", text="   Line Project", icon_value=brush_icons["line_project"])
        op.name = "builtin.line_project"


class PIE_MT_init_face_sets(Menu):
    bl_label = "Init Face Sets"
    bl_idname = "PIE_MT_init_face_sets"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        op = pie.operator("sculpt.face_sets_init", text='Loose Parts', icon="OUTLINER_DATA_POINTCLOUD")
        op.mode = 'LOOSE_PARTS'
        op = pie.operator("sculpt.face_sets_init", text='Face Set Boundaries', icon="PIVOT_BOUNDBOX")
        op.mode = 'FACE_SET_BOUNDARIES'
        op = pie.operator("sculpt.face_sets_init", text='Materials', icon="MATERIAL")
        op.mode = 'MATERIALS'
        op = pie.operator("sculpt.face_sets_init", text='Normals', icon="NORMALS_VERTEX_FACE")
        op.mode = 'NORMALS'
        op = pie.operator("sculpt.face_sets_init", text='UV Seams', icon="UV_EDGESEL")
        op.mode = 'UV_SEAMS'
        op = pie.operator("sculpt.face_sets_init", text='Edge Creases', icon="EDGESEL")
        op.mode = 'CREASES'
        op = pie.operator("sculpt.face_sets_init", text='Edge Bevel Weight', icon="MOD_BEVEL")
        op.mode = 'BEVEL_WEIGHT'
        op = pie.operator("sculpt.face_sets_init", text='Sharp Edges', icon="SHARPCURVE")
        op.mode = 'SHARP_EDGES'


classes = (
    PIE_MT_hide_mask_brushes,
    PIE_MT_init_face_sets,
)


from my_pie_menus import utils


kms = [
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Sculpt",
        "letter": "ONE",
        "shift": 0,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_init_face_sets"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Sculpt",
        "letter": "TWO",
        "shift": 0,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_hide_mask_brushes"},
    },
]

addon_keymaps = []


def register():
    create_icons()
    utils.register_classes(classes)
    utils.register_keymaps(kms, addon_keymaps)


def unregister():
    release_icons()

    for cls in classes:
        bpy.utils.unregister_class(cls)
        utils.unregister_keymaps(kms)
