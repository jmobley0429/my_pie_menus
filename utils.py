import bpy
import bmesh
import math
import json

from pathlib import Path

PARENT_DIR = Path(__file__).parent


def get_active_obj():
    return bpy.context.active_object


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


class AddMannequin(bpy.types.Operator):
    bl_idname = "mesh.primitive_mannequin_add"
    bl_label = "Mannequin"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        file_path = PARENT_DIR / "resources" / 'mannequin.json'
        with open(file_path.resolve(), 'rb') as f:
            data = json.load(f)
        mesh = bpy.data.meshes.new("Mannequin")
        mesh.from_pydata(**data)
        bpy.data.objects.new("Mannequin", mesh)
        obj = bpy.data.objects["Mannequin"]
        bpy.context.collection.objects.link(obj)

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
