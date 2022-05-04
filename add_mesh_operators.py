import bpy
from .custom_operator import CustomOperator

MESH_CLASSES = {'Cube': 'mesh.primitive_cube_add', 'Cylinder': 'mesh.primitive_cylinder_add'}


class AddCustomMeshOperator(CustomOperator, bpy.types.Operator):
    bl_idname = 'object.add_custom_mesh'
    bl_label = 'Add Custom Mesh'

    @classmethod
    def poll(cls, context):
        return True

    type: bpy.props.StringProperty()
    size: bpy.props.FloatProperty()
    vertices: bpy.props.IntProperty()

    def execute(self, context):

        return {'FINISHED'}
