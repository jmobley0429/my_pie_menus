import bpy
from bpy.types import Menu


class SetSnap(bpy.types.Operator):
    bl_idname = "object.set_snap"
    bl_label = "Set Snap Option"

    type: bpy.props.StringProperty()

    def execute(self, context):
        scene = bpy.context.scene
        scene.tool_settings.snap_elements = {self.type}
        return {"FINISHED"}


class PIE_MT_SnapOptions(Menu):
    bl_idname = "PIE_MT_SnapOptions"
    bl_label = "Pie Snap Options"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator('object.set_snap', text="Increment", icon="SNAP_INCREMENT").type = 'INCREMENT'
        pie.operator('object.set_snap', text="Vertex", icon="SNAP_VERTEX").type = 'VERTEX'
        pie.operator('object.set_snap', text="Face", icon="SNAP_FACE").type = 'FACE'
        pie.operator('object.set_snap', text="Edge", icon="SNAP_EDGE").type = 'EDGE'
