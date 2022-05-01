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
