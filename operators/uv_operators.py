import bpy
import bmesh
from bpy.types import Operator
from mathutils import Vector

from .custom_operator import CustomBmeshOperator


class IMAGE_OT_snap_uvs_to_midpoint(CustomBmeshOperator, Operator):
    bl_idname = "uv.snap_uvs_to_midpoint"
    bl_label = "Snap UVs to Midpoint"
    bl_description = "Snap UVs to Midpoint"
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.EnumProperty(
        items=[
            ("x", "X", 'X-Axis'),
            ("y", "Y", 'Y-Axis'),
        ],
        name="Direction",
        description="Axis to align to midpoint on.",
        default="x",
    )
    bounds: bpy.props.EnumProperty(
        items=[
            ('MIN', 'Min Bounds', 'Snap min bounds to midpoint.'),
            ('MAX', 'Max Bounds', 'Snap max bounds to midpoint.'),
        ],
        name="Snap Bounds",
        description="Which side to snap to midpoint, far left or far right, etc.",
        default="MAX",
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object is not None
        area_type = context.area.type == "IMAGE_EDITOR"
        mode = "EDIT" in context.mode
        return all([obj, area_type, mode])

    @property
    def uv_vert_locs(self):
        return [loop.uv for loop in self.selected_uvs]

    @property
    def get_vert_locs_extent(self):
        if self.direction == "x":
            verts = [uv.x for uv in self.uv_vert_locs]
        else:
            verts = [uv.y for uv in self.uv_vert_locs]
        if self.bounds == "MIN":
            return min(verts)
        else:
            return max(verts)

    @property
    def deltas(self):
        deltas = []
        bounds = self.get_vert_locs_extent
        delta = 0.5 - bounds
        if self.direction == "x":
            delta = Vector((delta, 0.0))
        else:
            delta = Vector((0.0, delta))
        for loop in self.selected_uvs:
            new_loc = loop.uv + delta
            deltas.append(new_loc)
        return deltas

    @property
    def selected_uvs(self):
        selected_uvs = []
        try:
            faces = self.bm.faces[:]
        except ReferenceError:
            self.set_bmesh()
        for face in self.bm.faces:
            for loop in face.loops:
                loop_uv = loop[self.uv_layer]
                if loop_uv.select:
                    selected_uvs.append(loop_uv)
        return selected_uvs

    def set_bmesh(self):
        self.obj = self.context.edit_object
        self.mesh = self.context.edit_object.data
        self.bm = bmesh.from_edit_mesh(self.mesh)

    def execute(self, context):
        self.bmesh(context)
        self.context = context
        self.uv_layer = self.bm.loops.layers.uv.verify()
        for loop, delta in zip(self.selected_uvs, self.deltas):
            loop.uv = delta
        bmesh.update_edit_mesh(self.mesh)
        return {"FINISHED"}


class IMAGE_OT_pack_with_mode(Operator):
    bl_idname = "uv.pack_with_mode"
    bl_label = "Pack"
    bl_description = "UVPackmaster Pack (ALT to use Blender Default Pack)"
    bl_options = {'REGISTER', 'UNDO'}

    mode = None

    def invoke(self, context, event):
        if event.alt:
            self.mode = "DEFAULT"
        return self.execute(context)

    def execute(self, context):
        if self.mode is None:
            bpy.ops.uvpackmaster2.uv_pack()
        else:
            bpy.ops.uv.pack_islands()
        return {"FINISHED"}


class IMAGE_OT_toggle_uv_sync_selection(Operator):
    bl_idname = "uv.toggle_uv_sync_selection"
    bl_label = "Toggle Sync"
    bl_description = "Toggle Sync"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object is not None
        area_type = context.area.type == "IMAGE_EDITOR"
        mode = "EDIT" in context.mode
        return all([obj, area_type, mode])

    def execute(self, context):
        tools = context.scene.tool_settings
        bpy.context.scene.tool_settings.use_uv_select_sync = not tools.use_uv_select_sync
        return {"FINISHED"}


classes = [
    IMAGE_OT_snap_uvs_to_midpoint,
    IMAGE_OT_toggle_uv_sync_selection,
    IMAGE_OT_pack_with_mode,
]


from my_pie_menus import utils

kms = []


def register():

    utils.register_classes(classes)
    utils.register_keymaps(kms)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        utils.unregister_keymaps(kms)
