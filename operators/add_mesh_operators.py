import bpy
import bpy
import bmesh
from mathutils import Quaternion, Vector, Matrix
from bpy_extras.object_utils import AddObjectHelper
from bpy_extras import object_utils


from mathutils import Euler
import json

from pathlib import Path

from .custom_operator import CustomOperator


class AddMannequin(bpy.types.Operator):
    bl_idname = "mesh.primitive_mannequin_add"
    bl_label = "Mannequin"
    bl_options = {"REGISTER", "UNDO"}

    PARENT_DIR = Path(__file__).parent.parent
    file_path = PARENT_DIR / "resources" / 'mannequin.json'

    @property
    def mannequin_name(self):

        objs = bpy.context.collection.objects
        names = sorted([obj.name for obj in objs if "Mannequin" in obj.name])
        if not names:
            return "Mannequin"
        else:
            last_name = names[-1]
            if "." in last_name:
                num = last_name.split('.')[1]
                num = int(num) + 1
            else:
                num = 1
            return f"Mannequin.{str(num).zfill(3)}"

    def _get_mesh_data(self):
        with open(self.file_path, 'rb') as f:
            mesh_data = json.load(f)
        mesh = bpy.data.meshes.new(self.mannequin_name)
        mesh.from_pydata(**mesh_data)
        return mesh

    @staticmethod
    def _handle_transforms(obj):
        rot = Euler((1.5708, 0, 0))
        obj.rotation_euler.rotate(rot)
        init_z_dim = obj.dimensions.z
        multiplier = 1.9 / init_z_dim
        obj.dimensions *= multiplier

    @staticmethod
    def _place_in_scene(obj, context):
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        bpy.context.object.select_set(True)

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        bpy.ops.object.shade_smooth()
        bpy.ops.object.pivotobottom()
        cursor_loc = bpy.context.scene.cursor.location
        obj.location = cursor_loc

    def execute(self, context):
        mesh = self._get_mesh_data()
        bpy.data.objects.new(self.mannequin_name, mesh)
        obj = bpy.data.objects[self.mannequin_name]
        self._handle_transforms(obj)
        self._place_in_scene(obj, context)
        return {'FINISHED'}


class CustomAddCube(bpy.types.Operator, AddObjectHelper):
    """Add a simple box mesh"""

    bl_idname = "mesh.custom_cube_add"
    bl_label = "Add Box"
    bl_options = {'REGISTER', 'UNDO'}

    size: bpy.props.FloatProperty(
        name="Size",
        description="Box Size",
        min=0.01,
        max=100.0,
        default=1.0,
    )

    def execute(self, context):
        mesh = bpy.data.meshes.new("Cube")
        bm = bmesh.new()
        geom = bmesh.ops.create_cube(bm, size=self.size)
        translate = self.size / 2
        for vert in geom['verts']:
            vert.co.z += translate
        bm.to_mesh(mesh)
        mesh.update()
        object_utils.object_data_add(context, mesh, operator=self)

        return {'FINISHED'}


class CustomAddCylinder(bpy.types.Operator, AddObjectHelper):
    """Add a simple cylinder mesh"""

    bl_idname = "mesh.custom_cylinder_add"
    bl_label = "Add Cylinder"
    bl_options = {'REGISTER', 'UNDO'}

    size: bpy.props.FloatProperty(
        name="Size",
        description="Cylinder Size",
        min=0.01,
        max=100.0,
        default=1.0,
    )

    def execute(self, context):
        mesh = bpy.data.meshes.new("Cylinder")
        bm = bmesh.new()
        geom = bmesh.ops.create_cylinder(bm, size=self.size)
        translate = self.size / 2
        for vert in geom['verts']:
            vert.co.z += translate
        bm.to_mesh(mesh)
        mesh.update()
        object_utils.object_data_add(context, mesh, operator=self)

        return {'FINISHED'}


classes = [
    AddMannequin,
    CustomCubeAdd,
    CustomCylinderAdd,
]
