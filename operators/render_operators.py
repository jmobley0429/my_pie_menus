import bpy
from bpy.types import Operator


class RENDER_OT_BakeEeveeScene(Operator):
    bl_idname = "render.rebake_eevee_scene"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Rebake EEVEE Scene"
    bl_description = "Simultaneously Bakes EEVEE Reflections and Indirect Lighting"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"
    
    def execute(self, context):
        bpy.ops.scene.light_cache_bake()
        bpy.ops.scene.light_cache_bake(subset='CUBEMAPS')
        return {"FINISHED"}
      


classes = [
    RENDER_OT_BakeEeveeScene,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()




