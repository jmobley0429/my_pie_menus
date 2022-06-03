import bpy
from bpy.types import Menu


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


def register():
    bpy.utils.register_class(OBJECT_MT_object_io_menu)


def unregister():
    bpy.utils.unregister_class(OBJECT_MT_object_io_menu)


if __name__ == "__main__":
    register()
