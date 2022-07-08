import bpy
import bmesh
import math
import json
import re
from mathutils import Euler
from collections import defaultdict
from pathlib import Path

from .custom_operator import CustomOperator


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


class AddLightSetup(CustomOperator, bpy.types.Operator):
    bl_idname = "object.add_light_setup"
    bl_label = "Add 3-Point Lighting Setup"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def _get_last_light():
        lights.append(bpy.data.objects[-1])

    @staticmethod
    def add_light(location, name, energy, target_obj, color, size):
        bpy.ops.object.light_add(type="AREA", location=location)
        key = last_light()
        key.name = name
        key.energy = energy
        key.color = color
        key.size = size
        light_obj = bpy.context.objectz
        light_obj.constraints.new(type="TRACK_TO")
        mod = last_constraint(light_obj)
        mod.target = obj

    def execute(self, context):
        obj = self.get_active_obj()
        bpy.ops.object.empty_add(type="CIRCLE", location=obj.location)
        track_obj = self.get_active_obj()
        track_obj.name = "Tracker"

        obj_w, obj_d, obj_h = obj.dimensions
        ox, oy, oz = obj.location

        key_loc = obj.dimensions.copy() * 1.2
        key_loc.y *= -1
        key_size = obj.dimensions.x * 0.75
        key_power = 125

        fill_loc = key_loc.copy() * 1.2
        fill_loc.x *= -1
        fill_loc.z *= 0.5
        fill_size = key_size * 2.5
        fill_power = key_power * 0.5

        rim_loc = key_loc.copy().cross(obj.location) * 0.75
        rim_loc.z *= 0.1
        rim_loc.y *= -1
        rim_power = key_power * 2
        rim_size = key_size * 0.3
        rim_color = (1, 1, 1)

        lights = []
        self.add_light(
            key_loc, name="Key", energy=key_power, target_obj=track_obj, color=(1, 0.94, 0.88), size=key_size
        )
        _get_last_light()
        self.add_light(
            fill_loc, name="Fill", energy=fill_power, target_obj=track_obj, color=(0.33, 0.80, 1), size=fill_size
        )
        _get_last_light()
        self.add_light(
            rim_loc, name="Rim", energy=rim_power, target_obj=track_obj, color=(0.33, 0.80, 1), size=rim_size
        )
        _get_last_light()

        for l in lights:
            l.parent = track_obj

        return {'FINISHED'}

    def menu_func(self, context):
        self.layout.operator(self.bl_idname, text=self.bl_label)


class SetCustomBatchName(bpy.types.Operator):

    bl_idname = "object.set_custom_batch_name"
    bl_label = "Set Custom Batch Name"

    name_string: bpy.props.StringProperty(name="New Name")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        objs = context.selected_objects
        for obj in objs:
            obj.name = self.name_string
        for obj in objs:
            obj.name = obj.name.replace('.0', "_")
        return {'FINISHED'}


class JG_SetUVChannels(bpy.types.Operator):

    bl_idname = "object.jg_set_uv_channels"
    bl_label = "Set JG UV Channels"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        objs = context.selected_objects
        obj_data = []
        for obj in objs:
            bpy.context.view_layer.objects.active = obj
            mesh = obj.data
            uvs = mesh.uv_layers
            for i, u in enumerate(uvs):
                if i > 0:
                    mesh.uv_layers.active_index = i
                    bpy.ops.mesh.uv_texture_remove()

        for obj in objs:
            mesh = obj.data
            if mesh not in obj_data:
                obj_data.append(mesh)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.mesh.uv_texture_add()
                uvs = mesh.uv_layers
                for i, u in reversed(list(enumerate(uvs))):
                    name = f"UV_Channel_{i+1}"
                    u.name = name
            else:
                continue

        return {'FINISHED'}


import bpy
from mathutils import Vector


class MESH_OT_chunk_slicer(bpy.types.Operator):
    """Slice object into chunks"""

    bl_idname = "object.chunk_slicer"
    bl_label = "Chunk Slicer"

    bl_options = {'REGISTER', "UNDO"}

    cell_size: bpy.props.FloatProperty(
        name="Cell Size",
        description="Distance between each slice.",
        default=0.3,
    )
    cleanup_threshold: bpy.props.FloatProperty(
        name="Cleanup Threshold",
        description="Size of objects dimensions to delete after slice operation.",
        default=0.005,
        precision=4,
    )
    reset_origins: bpy.props.BoolProperty(
        name="Reset Origins",
        description="Set new chunk object origins to geometry center",
        default=False,
    )
    x: bpy.props.BoolProperty(
        name="X Axis",
        description="Slice on the X axis",
        default=True,
    )
    y: bpy.props.BoolProperty(
        name="Y Axis",
        description="Slice on the Y axis",
        default=True,
    )
    z: bpy.props.BoolProperty(
        name="Z Axis",
        description="Slice on the Z axis",
        default=True,
    )

    axes = list('xyz')

    @property
    def num_axes_selected(self):
        return sum([self.x, self.y, self.z])

    def _get_plane_co(self, axis):
        co = [0, 0, 0]
        index = self.axes.index(axis)
        co[index] = self.current_loc
        return co

    def _get_plane_no(self, axis):
        plane_nos = {
            'x': Vector((1, 0, 0)),
            'y': Vector((0, 1, 0)),
            'z': Vector((0, 0, 1)),
        }
        return Vector(plane_nos[axis])

    def _slices_in_axis(self, axis):
        return int(getattr(self.num_slices, axis))

    def _bmesh(cls, context):
        obj = context.obj
        mesh = obj.data
        self.bm = bmesh.new()
        self.bm.from_mesh(mesh)

    def _get_start_loc(self, axis):
        loc = min([getattr(v.co, axis) for v in self.obj.data.vertices])
        return loc

    def _get_slice_index(self, axis, index):
        return self.slice_locs[axis][index]

    def _mesh_has_manifold_geom(self):
        return all([e.is_manifold for e in self.bm.edges[:]])

    def _rename_temp(self, object):
        object.name = f"__Sliced__{self.current_index}"

    def _duplicate_obj(self, context):
        new_obj = self.obj.copy()
        new_obj.data = self.obj.data.copy()
        self._rename_temp(new_obj)
        context.collection.objects.link(new_obj)
        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = new_obj
        self.current_obj = new_obj

    def _slice(self, axis, clear_inner=False, clear_outer=False):
        self.current_obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.bisect(
            plane_co=self._get_plane_co(axis),
            plane_no=self._get_plane_no(axis),
            clear_inner=clear_inner,
            clear_outer=clear_outer,
            use_fill=True,
        )
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")

    def slice_operation_(self, context):
        self._duplicate_obj(context)
        axis = self.current_axis
        i = self.current_index
        if i != 0:
            old_loc = self.current_loc
            self.current_loc = self.slice_locs[axis][i - 1]
            self._slice(axis, clear_inner=True)
            self.current_loc = old_loc
        if i != self._slices_in_axis(axis):
            self._slice(axis, clear_outer=True)

    def _invalid_dimensions(self, dims):
        invalid = sum([v <= self.cleanup_threshold for v in dims]) > 1

        if invalid:
            print("Invalid Dims: ", dims)
            print([v < self.cleanup_threshold for v in dims])
            for d in dims:
                print(f"{d} < {self.cleanup_threshold}")
        return

    def _cleanup_objs(self, context):
        context.scene.objects.update()
        objs = context.view_layer.objects
        bpy.ops.object.select_all(action="DESELECT")
        cleanup_objs = [obj for obj in objs if "__Sliced__" in obj.name]
        orig_name = re.sub("(\.\d+$)", '', self.orig_name)
        for obj in cleanup_objs:
            dims = obj.dimensions
            if not obj.data.vertices[:] or self._invalid_dimensions(dims):
                context.collection.objects.unlink(obj)
                cleanup_objs.remove(obj)

        for i, obj in enumerate(cleanup_objs):
            if self.reset_origins:
                obj.select_set(True)
            new_name = f"{orig_name}_Sliced_{i+1}"
            obj.name = new_name
        if self.reset_origins:
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        bpy.ops.object.select_all(action="DESELECT")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH" and context.mode == "OBJECT"

    def invoke(self, context, event):
        self.obj = context.active_object
        self.orig_name = self.obj.name
        self.mesh = self.obj.data
        self.bm = bmesh.new()
        self.bm.from_mesh(self.mesh)
        if not (self._mesh_has_manifold_geom()):
            self.report(
                {"WARNING"}, "Mesh must have manifold geometry to perform slice operation. Operation Cancelled."
            )
            return {"CANCELLED"}
        self.dims = self.obj.dimensions
        self.num_slices = Vector([dim // self.cell_size for dim in self.dims])
        self.slice_locs = defaultdict(list)
        for axis in self.axes:
            current_loc = self._get_start_loc(axis)
            for i in range(self._slices_in_axis(axis) + 1):
                new_loc = current_loc + self.cell_size
                self.slice_locs[axis].append(new_loc)
                current_loc = new_loc
        self.current_obj = self.obj
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        sliced_x = []
        sliced_y = []

        if self.num_axes_selected == 0:
            self.report({"ERROR"}, "Must select at least one slice axis.")
            return {"CANCELLED"}
        if self.x:
            self.current_axis = "x"
            x_locs = self.slice_locs[self.current_axis]
            for index, loc in enumerate(x_locs):
                self.current_loc = loc
                self.current_index = index
                self.slice_operation_(context)
                sliced_x.append(self.current_obj)
            self.obj.hide_set(True)
            self.obj.name = "Sliced_Original"
        if self.y:
            self.current_axis = "y"
            y_locs = self.slice_locs[self.current_axis]
            if not sliced_x:
                sliced_x = [self.obj]
            for obj in sliced_x:
                self.obj = obj
                for index, loc in enumerate(y_locs):
                    self.current_loc = loc
                    self.current_index = index
                    self.slice_operation_(context)
                    sliced_y.append(self.current_obj)
                context.collection.objects.unlink(obj)
        if self.z:
            self.current_axis = "z"
            z_locs = self.slice_locs[self.current_axis]
            if not sliced_y:
                if not sliced_x:
                    sliced_y = [self.obj]
                else:
                    sliced_y = sliced_x
            for obj in sliced_y:

                self.obj = obj
                for index, loc in enumerate(z_locs):
                    self.current_loc = loc
                    self.current_index = index
                    self.slice_operation_(context)
                    # sliced_y.append(self.current_obj)
                context.collection.objects.unlink(obj)

        self._cleanup_objs(context)
        return {'FINISHED'}


classes = (
    AddCameraCustom,
    AddLightSetup,
    SetCustomBatchName,
    MESH_OT_chunk_slicer,
    # delete later
    JG_SetUVChannels,
)
