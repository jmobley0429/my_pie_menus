import bpy
import bpy
import bmesh
from mathutils import Quaternion, Vector, Matrix
from bpy_extras.object_utils import AddObjectHelper
from bpy_extras import object_utils


from mathutils import Euler
import json

from pathlib import Path

from .custom_operator import *


class AddMannequin(CustomOperator, bpy.types.Operator):
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
        # rot = Euler((1.5708, 0, 0))
        # obj.rotation_euler.rotate(rot)
        init_z_dim = obj.dimensions.z
        multiplier = 1.9 / init_z_dim
        obj.dimensions *= multiplier

    def _place_in_scene(self, context, obj):
        prev_select = context.selected_objects
        bpy.ops.object.select_all(action="DESELECT")
        context.collection.objects.link(obj)
        self.set_active_and_selected(context, obj)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        bpy.ops.object.shade_smooth()
        bpy.ops.object.pivotobottom()
        cursor_loc = bpy.context.scene.cursor.location
        obj.location = cursor_loc
        self.select_objects_in_list(prev_select)

    def execute(self, context):
        mesh = self._get_mesh_data()
        bpy.data.objects.new(self.mannequin_name, mesh)
        obj = bpy.data.objects[self.mannequin_name]
        self._handle_transforms(obj)
        self._place_in_scene(context, obj)
        return {'FINISHED'}


class CustomCubeAdd(CustomBmeshOperator, bpy.types.Operator, AddObjectHelper):
    """Add a simple cube mesh"""

    bl_idname = "mesh.custom_cube_add"
    bl_label = "Add Cube"
    bl_options = {'REGISTER', 'UNDO'}

    size: bpy.props.FloatProperty(
        name="Size",
        description="Cube Size",
        min=0.01,
        max=100.0,
        default=1.0,
    )

    center_origin = True

    def invoke(self, context, event):
        if event.alt:
            self.center_origin = False
        return self.execute(context)

    def execute(self, context):
        self.new_bmesh("Cube")
        geom = bmesh.ops.create_cube(self.bm, size=self.size)
        if not self.center_origin:
            translate = self.size / 2
            for vert in geom['verts']:
                vert.co.z += translate
        self.bm.to_mesh(self.mesh)
        self.mesh.update()
        object_utils.object_data_add(context, self.mesh, operator=self)
        return {'FINISHED'}


class CustomCylinderAdd(CustomBmeshOperator, bpy.types.Operator, AddObjectHelper):
    """Add a simple cylinder mesh"""

    bl_idname = "mesh.custom_cylinder_add"
    bl_label = "Add Cylinder"
    bl_options = {'REGISTER', 'UNDO'}

    radius: bpy.props.FloatProperty(
        name="Radius",
        description="Cylinder Radius",
        default=0.5,
    )
    height: bpy.props.FloatProperty(
        name="Height",
        description="Cylinder Height",
        default=1.0,
    )
    vertices: bpy.props.IntProperty(
        name="Vertices",
        description="Vertex Count",
        default=16,
    )

    center_origin = True

    def invoke(self, context, event):
        if event.alt:
            self.center_origin = False
        return self.execute(context)

    def execute(self, context):
        self.new_bmesh("Cylinder")
        bmesh.ops.create_circle(self.bm, cap_ends=True, radius=self.radius, segments=self.vertices)
        faces = self.bm.faces[:]
        ret = bmesh.ops.extrude_face_region(self.bm, geom=faces)
        new_verts = [v for v in ret['geom'] if self.is_vert(v)]
        del ret
        vec = Vector((0, 0, self.height))
        bmesh.ops.translate(
            self.bm,
            vec=vec,
            verts=new_verts,
        )
        if self.center_origin:
            translate = self.height / 2
            for vert in self.bm.verts[:]:
                vert.co.z -= translate

        self.bm.to_mesh(self.mesh)
        self.mesh.update()
        object_utils.object_data_add(context, self.mesh, operator=self)
        return {'FINISHED'}


classes = [
    AddMannequin,
    CustomCubeAdd,
    CustomCylinderAdd,
]
