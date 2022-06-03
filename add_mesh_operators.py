import bpy

from pathlib import Path

from .custom_operator import CustomOperator


class AddMannequin(bpy.types.Operator):
    bl_idname = "mesh.primitive_mannequin_add"
    bl_label = "Mannequin"
    bl_options = {"REGISTER", "UNDO"}

    PARENT_DIR = Path(__file__).parent
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
