import bpy
from bpy.types import Menu


class MESH_MT_select_linked_pie(Menu):
    bl_label = "Select Linked"
    bl_idname = "MESH_MT_select_linked_pie"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator_enum('mesh.select_linked', "delimit")
        op = pie.operator('mesh.select_all', text="Invert")
        op.action = "INVERT"

def register():
    bpy.utils.register_class(MESH_MT_select_linked_pie)


def unregister():
    bpy.utils.unregister_class(MESH_MT_select_linked_pie)


if __name__ == "__main__":
    register()
