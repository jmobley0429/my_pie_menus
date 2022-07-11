import bpy
import bmesh
import math
import json
import re
from mathutils import Euler, Vector
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


class OBJECT_OT_sort_items_on_axis(bpy.types.Operator):

    bl_idname = "object.sort_objects_on_axis"
    bl_label = "Sort Objects on Axis"
    bl_options = {"REGISTER", "UNDO"}

    axis: bpy.props.EnumProperty(
        name="Axis",
        description="Axis to array items.",
        items=[
            ('x', 'X', "X-Axis"),
            ('y', 'Y', "Y-Axis"),
            ('z', 'Z', "Z-Axis"),
        ],
        default='x',
    )
    spacing_multiplier: bpy.props.FloatProperty(name="Spacing", default=1.5)
    grid_offset: bpy.props.IntProperty(name="Grid Offset", default=6)
    grid_axis: bpy.props.EnumProperty(
        name="Grid Axis",
        description="Axis on which to array items on a grid",
        items=[
            ('x', 'X', "X-Axis"),
            ('y', 'Y', "Y-Axis"),
            ('z', 'Z', "Z-Axis"),
        ],
        default='y',
    )
    initial_loc = Vector((0, 0, 0))

    axes = list('xyz')

    def get_obj_dim(self, obj):
        return getattr(obj.dimensions, self.axis)

    def get_grid_offset(self):
        return max([self.get_obj_dim(obj) for obj in self.objs])

    @property
    def prev_obj(self):
        if self.current_index == 0:
            return self.objs[0]
        else:
            return self.objs[self.current_index - 1]

    @property
    def current_obj(self):
        return self.objs[self.current_index]

    def get_new_loc_tuple(self, loc):
        coord = [0] * 3
        index = self.axes.index(self.axis)
        coord[index] = loc
        return Vector(coord)

    def calc_obj_loc(self):
        obj_dim = self.get_obj_dim(self.current_obj)
        prev_dim = self.get_obj_dim(self.prev_obj)
        return self.get_new_loc_tuple(((obj_dim + prev_dim) / 2) * self.spacing_multiplier)

    def cycle_axis(self, event, axis, axis_type="axis"):
        current_axis_index = self.axes.index(axis)
        if event.shift:
            new_ax = self.axes[current_axis_index - 1]
        else:
            new_ax = self.axes[current_axis_index + 1]
        setattr(self, axis_type, new_ax)

    def arrange_objs(self):
        self.current_index = 0
        first_loc = self.initial_loc
        for obj in self.objs:
            if self.current_index == 0:
                obj.location = first_loc
            else:
                new_loc = self.calc_obj_loc()
                first_loc += new_loc
                print(f"First loc after x mod: {first_loc}")
                if self.current_index % self.grid_offset == 0:
                    old_ax = self.axis
                    self.axis = self.grid_axis
                    grid_loc = self.get_new_loc_tuple(self.get_grid_offset())
                    old_axis_orig = getattr(self.cursor_loc, old_ax)
                    print(f"OLD:{old_axis_orig}")
                    setattr(first_loc, old_ax, old_axis_orig)

                    first_loc += grid_loc

                    print(f"GRID_LOC: {grid_loc}, FIRST_LOC: {first_loc}")
                    self.axis = old_ax
                obj.location = first_loc
            self.current_index += 1

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.selected_objects

    def invoke(self, context, event):

        return context.window_manager.invoke_props_popup(self, event)

    def execute(self, context):
        self.objs = context.selected_objects
        self.original_locations = [obj.location for obj in self.objs]
        self.num_objs = len(self.objs)
        self.cursor_loc = context.scene.cursor.location.copy()
        self.initial_loc = self.cursor_loc.copy()

        self.arrange_objs()

        return {'FINISHED'}


classes = (
    AddCameraCustom,
    AddLightSetup,
    SetCustomBatchName,
    # delete later
    JG_SetUVChannels,
    OBJECT_OT_sort_items_on_axis,
)
