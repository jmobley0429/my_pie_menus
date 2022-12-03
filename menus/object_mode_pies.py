from my_pie_menus import utils
import bpy
from bpy.types import Menu
from my_pie_menus.operators import object_mode_operators as omo


class PIE_MT_ConvertMeshCurve(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Convert Mesh/Curve"
    bl_idname = "PIE_MT_ConvertMeshCurve"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator_enum("object.convert", "target")


class PIE_MT_sort_objects(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Align Objects on Axis"
    bl_idname = "PIE_MT_sort_objects"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        box = pie.box()
        box.label(text="Arrange")
        col = box.column()
        spl = col.split()
        op = spl.operator("object.sort_objects_on_axis", text="X")
        op.axis = 'x'
        op.align_to = "GRID"
        op = spl.operator("object.sort_objects_on_axis", text="Y")
        op.axis = 'y'
        op.grid_axis = 'x'
        op.align_to = "GRID"
        op = spl.operator("object.sort_objects_on_axis", text="Z")
        op.axis = 'z'
        op.align_to = "GRID"

        box = pie.box()
        box.label(text="Sort Along Axis")
        col = box.column(align=True)
        spl = col.split()
        op = spl.operator("object.sort_objects_on_axis", text="X")
        op.axis = 'x'
        op.align_to = "ROW"
        op = spl.operator("object.sort_objects_on_axis", text="Y")
        op.axis = 'y'
        op.align_to = "ROW"
        op = spl.operator("object.sort_objects_on_axis", text="Z")
        op.axis = 'z'
        op.align_to = "ROW"
        #
        box = pie.box()
        box.label(text="Align to Cursor")
        col = box.column(align=True)
        spl = col.split()
        spl = col
        op = spl.operator("object.align_objects", text="X")
        op.axis = 'x'
        op.align_to = "CURSOR"
        op = spl.operator("object.align_objects", text="Y")
        op.axis = 'y'
        op.align_to = "CURSOR"
        spl = col.split()
        op = spl.operator("object.align_objects", text="Z")
        op.axis = 'z'
        op.align_to = "CURSOR"

        box = pie.box()
        box.label(text="Align to Active")
        col = box.column(align=True)
        # spl = col.split()
        spl = col
        op = spl.operator("object.align_objects", text="X")
        op.axis = 'x'
        op.align_to = "ACTIVE"
        op = spl.operator("object.align_objects", text="Y")
        op.axis = 'y'
        op.align_to = "ACTIVE"
        spl = col.split()
        op = spl.operator("object.align_objects", text="Z")
        op.axis = 'z'
        op.align_to = "ACTIVE"

        box = pie.box()
        box.label(text="Align to Neg")
        col = box.column(align=True)
        spl = col.split()
        op = spl.operator("object.align_objects", text="X")
        op.axis = 'x'
        op.align_to = "NEG"
        op = spl.operator("object.align_objects", text="Y")
        op.axis = 'y'
        op.align_to = "NEG"
        op = spl.operator("object.align_objects", text="Z")
        op.axis = 'z'
        op.align_to = "NEG"

        box = pie.box()
        box.label(text="Align to Pos")
        col = box.column(align=True)
        spl = col.split()
        op = spl.operator("object.align_objects", text="X")
        op.axis = 'x'
        op.align_to = "POS"
        op = spl.operator("object.align_objects", text="Y")
        op.axis = 'y'
        op.align_to = "POS"
        op = spl.operator("object.align_objects", text="Z")
        op.axis = 'z'
        op.align_to = "POS"


class OBJECT_MT_object_io_menu(Menu):
    bl_label = "Object I/O"
    bl_idname = "OBJECT_MT_object_io_menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("import_scene.fbx", text="Import FBX")
        pie.operator("export_scene.fbx", text="Export FBX")
        pie.operator("import_scene.obj", text="Import OBJ")
        pie.operator("export_scene.obj", text="Export OBJ")


class OBJECT_MT_quick_transform_pie(Menu):
    bl_idname = "OBJECT_MT_quick_transform_pie"
    bl_label = "Quick Transform"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        box = pie.box()
        val = 90
        box.label(text=f"Rotate {val}")
        spl = box.split()
        op = spl.operator("object.quick_transform", text="X")
        op.axis = "X"
        op.transform_type = "Rotation"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Y")
        op.axis = "Y"
        op.transform_type = "Rotation"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Z")
        op.axis = "Z"
        op.transform_type = "Rotation"
        op.transform_amt = val

        box = pie.box()
        val = 22.5
        box.label(text=f"Rotate {val}")
        spl = box.split()
        op = spl.operator("object.quick_transform", text="X")
        op.axis = "X"
        op.transform_type = "Rotation"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Y")
        op.axis = "Y"
        op.transform_type = "Rotation"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Z")
        op.axis = "Z"
        op.transform_type = "Rotation"
        op.transform_amt = val

        box = pie.box()
        val = 45
        box.label(text=f"Rotate {val}")
        spl = box.split()
        op = spl.operator("object.quick_transform", text="X")
        op.axis = "X"
        op.transform_type = "Rotation"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Y")
        op.axis = "Y"
        op.transform_type = "Rotation"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Z")
        op.axis = "Z"
        op.transform_type = "Rotation"
        op.transform_amt = val

        box = pie.box()
        val = 180
        box.label(text=f"Rotate {val}")
        spl = box.split()
        op = spl.operator("object.quick_transform", text="X")
        op.axis = "X"
        op.transform_type = "Rotation"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Y")
        op.axis = "Y"
        op.transform_type = "Rotation"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Z")
        op.axis = "Z"
        op.transform_type = "Rotation"
        op.transform_amt = val

        # SCALE
        box = pie.box()
        val = 2
        box.label(text=f"Scale {val}x")
        row = box.row()
        op = row.operator("object.quick_transform", text="All")
        op.transform_amt = val
        op.axis = "ALL"
        op.transform_type = "Scale"
        row = box.row()
        spl = row.split()
        op = spl.operator("object.quick_transform", text="X")
        op.axis = "X"
        op.transform_type = "Scale"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Y")
        op.axis = "Y"
        op.transform_type = "Scale"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Z")
        op.axis = "Z"
        op.transform_type = "Scale"
        op.transform_amt = val

        # SCALE
        box = pie.box()
        val = 10
        box.label(text=f"Scale {val}x")
        row = box.row()
        op = row.operator("object.quick_transform", text="All")
        op.transform_amt = val
        op.axis = "ALL"
        op.transform_type = "Scale"
        row = box.row()
        spl = row.split()
        op = spl.operator("object.quick_transform", text="X")
        op.axis = "X"
        op.transform_type = "Scale"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Y")
        op.axis = "Y"
        op.transform_type = "Scale"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Z")
        op.axis = "Z"
        op.transform_type = "Scale"
        op.transform_amt = val
        # SCALE
        box = pie.box()
        val = 5
        box.label(text=f"Scale {val}x")
        box.scale_y *= 0.9
        row = box.row()
        op = row.operator("object.quick_transform", text="All")
        op.transform_amt = val
        op.axis = "ALL"
        op.transform_type = "Scale"
        row = box.row()
        spl = row.split()
        op = spl.operator("object.quick_transform", text="X")
        op.axis = "X"
        op.transform_type = "Scale"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Y")
        op.axis = "Y"
        op.transform_type = "Scale"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Z")
        op.axis = "Z"
        op.transform_type = "Scale"
        op.transform_amt = val
        box = pie.box()
        val = 4
        box.label(text=f"Scale {val}x")
        row = box.row()
        op = row.operator("object.quick_transform", text="All")
        op.transform_amt = val
        op.axis = "ALL"
        op.transform_type = "Scale"
        row = box.row()
        spl = row.split()
        op = spl.operator("object.quick_transform", text="X")
        op.axis = "X"
        op.transform_type = "Scale"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Y")
        op.axis = "Y"
        op.transform_type = "Scale"
        op.transform_amt = val
        op = spl.operator("object.quick_transform", text="Z")
        op.axis = "Z"
        op.transform_type = "Scale"
        op.transform_amt = val


def jake_tools_panel(context, layout):
    box = layout.box()
    box.label(text="Texturing Tools")
    col = box.column(align=True)
    col.label(text="Assign Random VCol")
    row = col.row(align=True)
    op = row.operator(
        omo.OBJECT_OT_generate_random_v_colors_per_obj.bl_idname, text="Single")
    op.multi_obj = False
    op = row.operator(
        omo.OBJECT_OT_generate_random_v_colors_per_obj.bl_idname, text="Multi Object")
    op.multi_obj = True
    col.separator()
    row = col.row()


class OBJECT_PT_jake_tools_panel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Jake Tools'
    bl_label = "Jake Tools"
    bl_idname = "OBJECT_PT_jake_tools_panel"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        jake_tools_panel(context, self.layout)


class VIEW3D_MT_PIE_toggle_view_transform(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Toggle View Transform"
    bl_idname = "VIEW3D_MT_PIE_toggle_view_transform"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        # operator_enum will just spread all available options
        # for the type enum of the operator on the pie
        pie.prop_enum(context.scene.view_settings, "view_transform", "Filmic")
        pie.prop_enum(context.scene.view_settings,
                      "view_transform", "False Color")


classes = (
    PIE_MT_ConvertMeshCurve,
    OBJECT_MT_object_io_menu,
    PIE_MT_sort_objects,
    OBJECT_MT_quick_transform_pie,
    VIEW3D_MT_PIE_toggle_view_transform,
    OBJECT_PT_jake_tools_panel,
)

kms = [
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Object Mode",
        "letter": "C",
        "shift": 0,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_ConvertMeshCurve"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Object Mode",
        "letter": "X",
        "shift": 0,
        "ctrl": 1,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_sort_objects"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Object Mode",
        "letter": "V",
        "shift": 0,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "VIEW3D_MT_PIE_toggle_view_transform"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Object Mode",
        "letter": "E",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "OBJECT_MT_object_io_menu"},
    },
]


addon_keymaps = []


def register():

    utils.register_classes(classes)
    utils.register_keymaps(kms, addon_keymaps)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        utils.unregister_keymaps(kms)
