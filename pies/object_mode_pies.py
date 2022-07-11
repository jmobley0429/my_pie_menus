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
    bl_label = "Sort Objects on Axis"
    bl_idname = "PIE_MT_sort_objects"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        op = pie.operator("object.sort_objects_on_axis", text="X")
        op.axis = 'x'
        op = pie.operator("object.sort_objects_on_axis", text="Y")
        op.axis = 'y'
        op = pie.operator("object.sort_objects_on_axis", text="Z")
        op.axis = 'z'


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
