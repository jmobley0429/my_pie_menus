import bpy
import bmesh
import math
import json
from mathutils import Euler

from pathlib import Path

ob_ops = bpy.ops.object

PARENT_DIR = Path(__file__).parent


def get_active_obj():
    return bpy.context.active_object


def clamp(value, min_num, max_num):
    return min(max_num, max(min_num, value))


class AddCameraCustom(bpy.types.Operator):
    bl_idname = "object.smart_add_camera"
    bl_label = "Smart Add Camera"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.camera_add(
            enter_editmode=False,
            align='VIEW',
            location=(0, 0, 0),
            rotation=(1.33911, 0.0142096, -0.524513),
            scale=(1, 1, 1),
        )
        bpy.ops.view3d.camera_to_view()
        return {'FINISHED'}


class AddMannequin(bpy.types.Operator):
    bl_idname = "mesh.primitive_mannequin_add"
    bl_label = "Mannequin"
    bl_options = {"REGISTER", "UNDO"}

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
    def _place_in_scene(obj):
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        bpy.context.object.select_set(True)
        ob_ops.transform_apply(location=True, rotation=True, scale=True)
        ob_ops.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        ob_ops.shade_smooth()
        ob_ops.pivotobottom()
        cursor_loc = bpy.context.scene.cursor.location
        obj.location = cursor_loc

    def execute(self, context):
        mesh = self._get_mesh_data()
        bpy.data.objects.new(self.mannequin_name, mesh)
        obj = bpy.data.objects[self.mannequin_name]
        self._handle_transforms(obj)
        self._place_in_scene(obj)
        return {'FINISHED'}


class AddLatticeCustom(bpy.types.Operator):
    bl_idname = "object.smart_add_lattice"
    bl_label = "Add Smart Lattice"
    bl_options = {"REGISTER", "UNDO"}

    @staticmethod
    def _get_uvw_res(coord_val):
        cpm = coord_val
        offset = 1
        if cpm < 1:
            cpm *= 100
            cpm = math.ceil(cpm)
        if cpm > 50:
            cpm //= 10
            cpm = math.ceil(cpm)
        return max(math.floor(cpm) + offset, 2)

    def execute(self, context):
        obj = get_active_obj()

        if obj:
            size = obj.dimensions
            loc = obj.matrix_world.translation

            bpy.ops.object.add(type="LATTICE", location=loc)
            lattice = get_active_obj()
            lattice.dimensions = size
            lattice.data.points_u = self._get_uvw_res(size.x)
            lattice.data.points_v = self._get_uvw_res(size.y)
            lattice.data.points_w = self._get_uvw_res(size.z)

        else:
            bpy.ops.object.add(type="LATTICE")

        return {'FINISHED'}
