import bpy
from bpy.types import Menu


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


classes = (
    PIE_MT_ConvertMeshCurve,
    OBJECT_MT_object_io_menu,
    PIE_MT_sort_objects,
)
