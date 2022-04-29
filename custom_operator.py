import bpy


class CustomOperator(bpy.types.Operator):
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def get_active_obj():
        return bpy.context.active_object
