import bpy
import bmesh
import math
import json
import re
from statistics import mean
from mathutils import Euler, Vector
from collections import defaultdict
from pathlib import Path
from bpy.types import Operator

from .custom_operator import CustomOperator, CustomModalOperator
from ..resources.utils import clamp


class AddCameraCustom(Operator):
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


class AddLightSetup(CustomOperator, Operator):
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


class SetCustomBatchName(Operator):

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


class JG_SetUVChannels(Operator):

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


class AlignOperator:
    axis: bpy.props.EnumProperty(
        name="Axis",
        description="Alignment Axis",
        items=[
            ('x', 'X', "X-Axis"),
            ('y', 'Y', "Y-Axis"),
            ('z', 'Z', "Z-Axis"),
        ],
        default='x',
    )
    align_to: bpy.props.EnumProperty(
        name="Axis",
        description="Where to align selected objects",
        items=[
            ('NEG', 'Negative', "Negative"),
            ('POS', 'Positive', "Positive"),
            ('CURSOR', 'Cursor', "Cursor"),
            ('ACTIVE', 'Active', "Active"),
            ('GRID', 'Active', "Active"),
            ("ROW", "Row", "Row"),
        ],
        default="GRID",
    )

    axes = list('xyz')

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.selected_objects

    def get_new_loc_tuple(self, loc):
        coord = [0] * 3
        index = self.axes.index(self.axis)
        coord[index] = loc
        return Vector(coord)

    def get_objs(self, context):
        return [obj for obj in context.selected_objects if obj.parent is None]


class OBJECT_OT_sort_items_on_axis(
    AlignOperator,
    CustomModalOperator,
    Operator,
):

    bl_idname = "object.sort_objects_on_axis"
    bl_label = "Sort Objects on Axis"
    bl_options = {"REGISTER", "UNDO"}

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
    sort_asc = None

    def get_obj_dim(self, obj):
        return getattr(obj.dimensions, self.axis)

    def get_grid_offset(self):
        return max([self.get_obj_dim(obj) for obj in self.objs])

    def set_grid_offset(self, addend):
        self.grid_offset = clamp(self.grid_offset + addend, 1, self.num_objs)

    @property
    def prev_obj(self):
        if self.current_index == 0:
            return self.objs[0]
        else:
            return self.objs[self.current_index - 1]

    @property
    def current_obj(self):
        return self.objs[self.current_index]

    @property
    def axis_string(self):
        return str(self.axis).upper().strip()

    @property
    def grid_axis_string(self):
        return str(self.grid_axis).upper().strip()

    @property
    def modal_info_string(self):
        if self.sort_asc is not None:
            type = "Descending"
            if self.sort_asc:
                type = "Ascending"
        else:
            type = "None"
        msg = [
            f"(Tab) AXIS: {self.axis_string}",
            f"(Mousewheel) SPACING MULTIPLIER: {self.spacing_multiplier:.2f}",
            f"(Ctrl + Mousewheel) GRID OFFSET: {self.grid_offset}",
            f"(G) GRID AXIS: {self.grid_axis_string}",
            f"(S) Sort Type: {type}",
        ]
        return ', '.join(msg)

    def calc_obj_loc(self):
        obj_dim = self.get_obj_dim(self.current_obj)
        prev_dim = self.get_obj_dim(self.prev_obj)
        return self.get_new_loc_tuple(((obj_dim + prev_dim) / 2) * self.spacing_multiplier)

    def cycle_axis(self, event, axis, axis_type="axis"):
        current_axis_index = self.axes.index(axis)
        if event.shift:
            new_ax = self.axes[current_axis_index - 1]
        else:
            new_ax = self.axes[(current_axis_index + 1) % len(self.axes)]
        setattr(self, axis_type, new_ax)

    def cycle_sort_asc(self, event):
        types = [None, False, True]
        current_type_index = types.index(self.sort_asc)
        if event.shift:
            new_type = types[current_type_index - 1]
        else:
            new_type = types[(current_type_index + 1) % len(self.axes)]
        setattr(self, "sort_asc", new_type)

    def arrange_objs(self, context):
        first_loc = self.initial_loc.copy()
        self.current_index = 0
        for obj in self.objs:
            # print(f"Arranging {obj.name}")
            if self.current_index == 0:
                obj.location = first_loc
            else:
                new_loc = self.calc_obj_loc()
                first_loc += new_loc
                # print(f"First loc after x mod: {first_loc}")
                if self.current_index % self.grid_offset == 0:
                    old_ax = self.axis
                    self.axis = self.grid_axis
                    grid_loc = self.get_new_loc_tuple(self.get_grid_offset())
                    old_axis_orig = getattr(self.cursor_loc, old_ax)
                    # print(f"OLD:{old_axis_orig}")
                    setattr(first_loc, old_ax, old_axis_orig)
                    first_loc += grid_loc
                    # print(f"GRID_LOC: {grid_loc}, FIRST_LOC: {first_loc}")
                    self.axis = old_ax
                obj.location = first_loc
            self.current_index += 1
        del first_loc

    def sort_objs_size(self, average=True):
        def get_obj_dims(obj):
            if average:
                return mean(obj.location)
            else:
                return getattr(obj.location, self.axis)

        if self.sort_asc is None:
            return self.original_obj_list
        return sorted(self.objs, key=lambda obj: get_obj_dims(obj), reverse=self.sort_asc)

    def invoke(self, context, event):
        self.objs = self.get_objs(context)
        self.original_obj_list = self.objs.copy()
        if event.alt:
            self.sort_asc = True
        elif event.ctrl:
            self.sort_asc = False
        self.objs = self.sort_objs_size()
        self.original_locations = [obj.location.copy() for obj in self.objs]
        self.num_objs = len(self.objs)
        self.cursor_loc = context.scene.cursor.location.copy()
        if self.align_to != "GRID":
            self.grid_offset = self.num_objs
            self.initial_loc = self.cursor_loc.copy()
            if self.align_to == "ACTIVE":
                self.initial_loc = context.active_object.location.copy()
            elif self.align_to in {"NEG", "POS"}:
                locs = sorted(self.original_locations, key=lambda x: getattr(x, self.axis))
                self.initial_loc = locs[-1]
                if self.align_to == "NEG":
                    self.initial_loc = locs[0]
            self.arrange_objs(context)
            return {"FINISHED"}
        else:
            self.grid_offset = int(self.num_objs // 2.5)
            self.spacing_multiplier = 1.9
            self.arrange_objs(context)
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}

    def modal(self, context, event):
        self.display_modal_info(self.modal_info_string, context)
        if event.value == "PRESS":
            if event.type == "TAB":
                self.cycle_axis(event, axis=self.axis)
            elif event.type == "G":
                self.cycle_axis(event, axis=self.grid_axis, axis_type="grid_axis")
            elif event.type == "WHEELUPMOUSE":
                if event.ctrl:
                    self.set_grid_offset(1)
                else:
                    self.spacing_multiplier += 0.1
            elif event.type == "WHEELDOWNMOUSE":
                if event.ctrl:
                    self.set_grid_offset(-1)
                else:
                    self.spacing_multiplier -= 0.1
            elif event.type in {"RIGHTMOUSE", "ESC"}:
                objs = self.get_objs(context)
                for obj, loc in zip(objs, self.original_locations):
                    obj.location = loc
                return self.exit_modal(context, cancelled=True)
            elif event.type == "LEFTMOUSE":
                return self.exit_modal(context)
            elif event.type == "S":
                self.cycle_sort_asc(event)
                self.objs = self.sort_objs_size()
            self.arrange_objs(context)
        return {"RUNNING_MODAL"}


class OBJECT_OT_align_objects(AlignOperator, Operator):
    bl_idname = "object.align_objects"
    bl_label = "Align Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        self.objs = self.get_objs(context)
        self.active_obj = context.active_object
        locs = [obj.location.copy() for obj in self.objs]
        if self.align_to in {'NEG', "POS"}:
            locs = [getattr(loc, self.axis) for loc in locs]
            if self.align_to == "NEG":
                self.align_loc = self.get_new_loc_tuple(min(locs))
            else:
                self.align_loc = self.get_new_loc_tuple(max(locs))
        elif self.align_to == "CURSOR":
            self.align_loc = context.scene.cursor.location.copy()
        elif self.align_to == "ACTIVE":
            self.align_loc = context.active_object.location.copy()
        return self.execute(context)

    def execute(self, context):
        loc_val = getattr(self.align_loc, self.axis)
        for obj in self.objs:
            setattr(obj.location, self.axis, loc_val)
        return {"FINISHED"}


class OBJECT_OT_set_auto_smooth_modal(CustomModalOperator, Operator):
    bl_idname = "object.auto_smooth_modal"
    bl_label = "Set Auto Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    @property
    def is_auto_smoothed(self):
        return self.me.use_auto_smooth

    @property
    def is_smooth_shaded(self):
        polys = self.me.polygons[:]
        return all([poly.use_smooth for poly in polys])

    def toggle_shading(self, context):
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
        bpy.ops.object.shade_smooth()
        self.me.use_auto_smooth = True
        self.me.auto_smooth_angle = math.radians(self.current_angle)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    @property
    def modal_info_string(self):
        if self.is_smooth_shaded:
            ss_msg = "Smooth"
        else:
            ss_msg = "Flat"
        msg = [
            f"AUTO SMOOTH ANGLE: {int(self.current_angle)}",
            f"USE CUSTOM SPLIT NORMALS: {self.me.has_custom_normals}",
            f"USE AUTO SMOOTH: {self.is_auto_smoothed}",
            f"SHADE MODE: {ss_msg}",
        ]

        return ', '.join(msg)

    def change_smoothing_angle(self, context, event, set_angle=False):
        if set_angle:
            self.me.auto_smooth_angle = math.radians(self.current_angle)
            return
        current_angle = math.degrees(self.me.auto_smooth_angle)
        addend = 5
        if event.shift:
            addend = 1
        divisor = addend
        if event.type == "WHEELDOWNMOUSE":
            addend *= -1
        raw_angle = current_angle + addend
        self.current_angle = round(raw_angle / divisor) * divisor
        self.me.auto_smooth_angle = math.radians(self.current_angle)

    def invoke(self, context, event):
        self.obj = context.active_object
        self.in_edit = self.in_mode(context, "EDIT")
        if self.in_edit:
            self.to_mode("OBJECT")
        self.current_angle = 40
        self.me = self.obj.data
        self.has_custom_normals = self.me.has_custom_normals
        self.initial_smoothing = self.is_smooth_shaded
        self.initial_auto_smoothing = self.is_auto_smoothed
        self.overlays_on = context.space_data.overlay.show_overlays
        if self.overlays_on:
            context.space_data.overlay.show_overlays = False
        self.toggle_shading(context)
        context.window_manager.modal_handler_add(self)
        print('running')
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.value == "PRESS":
            if event.type == "N":
                if self.me.has_custom_normals:
                    bpy.ops.mesh.customdata_custom_splitnormals_clear()
                else:
                    bpy.ops.mesh.customdata_custom_splitnormals_add()
            elif event.type == "TAB":
                self.me.use_auto_smooth = not self.is_auto_smoothed
            elif event.type == "S":
                self.toggle_shading(context)
            elif event.type == "LEFTMOUSE":
                context.space_data.overlay.show_overlays = self.overlays_on
                if self.in_edit:
                    self.to_mode("EDIT")
                return self.exit_modal(context)

            elif event.type in {"RIGHTMOUSE", "ESC"}:
                if not self.initial_smoothing:
                    bpy.ops.object.shade_flat()
                self.me.use_auto_smooth = self.initial_auto_smoothing
                context.space_data.overlay.show_overlays = self.overlays_on
                if self.in_edit:
                    self.to_mode("EDIT")
                return self.exit_modal(context, cancelled=True)
            elif event.type in {'WHEELUPMOUSE', "WHEELDOWNMOUSE"}:
                self.change_smoothing_angle(context, event)
            elif event.type in self.numpad_input:
                if event.type == "NUMPAD_ENTER":

                    self.current_angle = self.float_numpad_value
                    self.change_smoothing_angle(context, event, set_angle=True)
                    self.numpad_value = []
                else:
                    self.set_numpad_input(event)

        self.display_modal_info(self.modal_info_string, context)
        return {"RUNNING_MODAL"}


classes = (
    AddCameraCustom,
    AddLightSetup,
    SetCustomBatchName,
    # delete later
    JG_SetUVChannels,
    OBJECT_OT_sort_items_on_axis,
    OBJECT_OT_align_objects,
    OBJECT_OT_set_auto_smooth_modal,
)
