from my_pie_menus.resources import utils
import bpy
import bmesh
import json
import re
import os
import numpy as np
from mathutils import Euler, Vector
from collections import defaultdict
from pathlib import Path
from bpy.types import Operator

import utils

from .custom_operator import (
    CustomOperator,
    CustomModalOperator,
    CustomBmeshOperator,
    OperatorBaseClass,
)


class AddCameraCustom(Operator):
    bl_idname = "object.smart_add_camera"
    bl_label = "Smart Add Camera"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.camera_add(
            enter_editmode=False,
            align="VIEW",
            location=(0, 0, 0),
            rotation=(1.33911, 0.0142096, -0.524513),
            scale=(1, 1, 1),
        )
        bpy.ops.view3d.camera_to_view()
        return {"FINISHED"}


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
            key_loc,
            name="Key",
            energy=key_power,
            target_obj=track_obj,
            color=(1, 0.94, 0.88),
            size=key_size,
        )
        _get_last_light()
        self.add_light(
            fill_loc,
            name="Fill",
            energy=fill_power,
            target_obj=track_obj,
            color=(0.33, 0.80, 1),
            size=fill_size,
        )
        _get_last_light()
        self.add_light(
            rim_loc,
            name="Rim",
            energy=rim_power,
            target_obj=track_obj,
            color=(0.33, 0.80, 1),
            size=rim_size,
        )
        _get_last_light()

        for l in lights:
            l.parent = track_obj

        return {"FINISHED"}

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
        active_obj = context.active_object
        objs = list(set(context.selected_objects) - set([active_obj]))
        objs.insert(0, active_obj)
        for i, obj in enumerate(objs[:]):
            if obj.name == self.name_string:
                obj.name = "__temp__"
        for i, obj in enumerate(objs):
            new_name = f"{self.name_string}_{str(i+1).zfill(2)}"
            obj.name = new_name
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        # Edit first editable button in popup
        def row_with_icon(layout, icon):
            row = layout.row()
            row.activate_init = True
            row.label(icon=icon)
            return row

        mode = context.mode
        row = row_with_icon(layout, "OBJECT_DATAMODE")
        row.prop(self, "name_string")


class JG_SetUVChannels(Operator):
    bl_idname = "object.jg_set_uv_channels"
    bl_label = "Set JG UV Channels"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        objs = [obj for obj in context.selected_objects if obj.type == "MESH"]
        obj_data = []
        for obj in objs:
            bpy.context.view_layer.objects.active = obj
            mesh = obj.data
            if not mesh:
                continue
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

        return {"FINISHED"}


class AlignOperator:
    axis: bpy.props.EnumProperty(
        name="Axis",
        description="Alignment Axis",
        items=[
            ("x", "X", "X-Axis"),
            ("y", "Y", "Y-Axis"),
            ("z", "Z", "Z-Axis"),
        ],
        default="x",
    )
    align_to: bpy.props.EnumProperty(
        name="Axis",
        description="Where to align selected objects",
        items=[
            ("NEG", "Negative", "Negative"),
            ("POS", "Positive", "Positive"),
            ("CURSOR", "Cursor", "Cursor"),
            ("ACTIVE", "Active", "Active"),
            ("GRID", "Active", "Active"),
            ("ROW", "Row", "Row"),
        ],
        default="GRID",
    )

    axes = list("xyz")

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


class OBJECT_OT_sort_items_on_axis(AlignOperator, CustomModalOperator, Operator):
    bl_idname = "object.sort_objects_on_axis"
    bl_label = "Sort Objects on Axis"
    bl_options = {"REGISTER", "UNDO"}

    spacing_multiplier: bpy.props.FloatProperty(name="Spacing", default=1.5)
    grid_offset: bpy.props.IntProperty(name="Grid Offset", default=6)
    grid_axis: bpy.props.EnumProperty(
        name="Grid Axis",
        description="Axis on which to array items on a grid",
        items=[
            ("x", "X", "X-Axis"),
            ("y", "Y", "Y-Axis"),
            ("z", "Z", "Z-Axis"),
        ],
        default="y",
    )
    initial_loc = Vector((0, 0, 0))
    sort_asc = None

    def get_obj_dim(self, obj):
        return getattr(obj.dimensions, self.axis)

    def get_grid_offset(self):
        return max([self.get_obj_dim(obj) for obj in self.objs])

    def set_grid_offset(self, addend):
        self.grid_offset = np.clip(self.grid_offset + addend, 1, self.num_objs)

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
        return ", ".join(msg)

    def calc_obj_loc(self):
        obj_dim = self.get_obj_dim(self.current_obj)
        prev_dim = self.get_obj_dim(self.prev_obj)
        return self.get_new_loc_tuple(
            ((obj_dim + prev_dim) / 2) * self.spacing_multiplier
        )

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
                return np.mean(obj.location)
            else:
                return getattr(obj.location, self.axis)

        if self.sort_asc is None:
            return self.original_obj_list
        return sorted(
            self.objs, key=lambda obj: get_obj_dims(obj), reverse=self.sort_asc
        )

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
                locs = sorted(
                    self.original_locations, key=lambda x: getattr(x, self.axis)
                )
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
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        self.objs = self.get_objs(context)
        self.active_obj = context.active_object
        locs = [obj.location.copy() for obj in self.objs]
        if self.align_to in {"NEG", "POS"}:
            locs = [getattr(loc, self.axis) for loc in locs]
            if self.align_to == "NEG":
                self.align_loc = self.get_new_loc_tuple(min(locs))
            else:
                self.align_loc = self.get_new_loc_tuple(max(locs))
        elif self.align_to == "CURSOR":
            self.align_loc = context.scene.cursor.location.copy()
        else:
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
    bl_options = {"REGISTER", "UNDO"}

    @property
    def is_auto_smoothed(self):
        return self.me.use_auto_smooth

    @property
    def is_smooth_shaded(self):
        polys = self.me.polygons[:]
        return all([poly.use_smooth for poly in polys])

    def toggle_shading(self, context):
        if not self.is_smooth_shaded:
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            bpy.ops.object.shade_smooth()
            self.me.use_auto_smooth = True
            self.me.auto_smooth_angle = np.radians(self.current_angle)
        else:
            bpy.ops.object.shade_flat()

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
            f"AUTO SMOOTH ANGLE (Wheel): {int(self.current_angle)}",
            f"USE CUSTOM SPLIT NORMALS (N): {self.me.has_custom_normals}",
            f"USE AUTO SMOOTH (TAB): {self.is_auto_smoothed}",
            f"SHADE MODE (S): {ss_msg}",
        ]

        return ", ".join(msg)

    def change_smoothing_angle(self, context, event, set_angle=False):
        if set_angle:
            self.me.auto_smooth_angle = np.radians(self.current_angle)
            return
        current_angle = np.degrees(self.me.auto_smooth_angle)
        addend = 5
        if event.shift:
            addend = 1
        divisor = addend
        if event.type == "WHEELDOWNMOUSE":
            addend *= -1
        raw_angle = current_angle + addend
        self.current_angle = round(raw_angle / divisor) * divisor
        self.me.auto_smooth_angle = np.radians(self.current_angle)

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
        print("running")
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
            elif event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
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


class OBJECT_add_empty_at_objs_center(Operator):
    bl_idname = "object.add_empty_at_objs_center"
    bl_label = "Add Object at Objects Center"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def _add_object_and_parent(self, context, obj):
        matrix = obj.matrix_world
        center = utils.get_bbox_center(obj, matrix)
        bpy.ops.object.empty_add(type="SPHERE", location=center)
        empty = context.object
        empty.empty_display_size = 0.25
        utils.set_parent(obj, empty)

    def execute(self, context):
        obj = context.active_object
        objs = context.selected_objects

        if len(objs) > 1:
            centers = []
            for obj in objs:
                mx = obj.matrix_world
                center = utils.get_bbox_center(obj, mx)
                centers.append(center)

            centers = np.array(centers)
            objs_center = np.mean(centers, axis=0)
            bpy.ops.object.empty_add(location=objs_center)
            empty = context.object

            for obj in objs:
                orig_mxt = obj.matrix_world.translation.copy()
                obj.parent = empty
                obj.matrix_world.translation = orig_mxt

        else:
            self._add_object_and_parent(context, obj)

        return {"FINISHED"}


class OBJECT_OT_quick_transforms(CustomOperator, Operator):
    bl_idname = "object.quick_transform"
    bl_label = "Quick Transform"
    bl_options = {"REGISTER", "UNDO"}
    desc_lines = [
        "Quick transform an object by set amount",
        "CTRL - Multiply transform amount by -1.",
        "ALT - Transform amount = 1 / transform amount",
    ]
    bl_description = "\n".join(desc_lines)

    axis: bpy.props.EnumProperty(
        items=(
            ("X", "X", "X Axis"),
            ("Y", "Y", "Y Axis"),
            ("Z", "Z", "Z Axis"),
            ("ALL", "All", "All Axes"),
        ),
        name="Axis",
        description="Transform Axis",
        default=None,
    )
    transform_type: bpy.props.EnumProperty(
        items=(
            ("Scale", "Scale", "Scale"),
            ("Rotation", "Rotation", "Rotation"),
        ),
        name="Transform Type",
        description="Type of Transform",
        default=None,
    )
    transform_amt: bpy.props.FloatProperty(name="Transform Amount")

    @property
    def axis_as_vector(self):
        if self.axis == "ALL":
            return [1, 1, 1]
        vector = [0, 0, 0]
        i = list("XYZ").index(self.axis)
        vector[i] = 1
        return vector

    def rotate_object(self):
        deg = np.radians(self.transform_amt)
        setattr(self, "transform_amt", deg)
        mat_func = getattr(self.mx, self.transform_type)
        transform_matrix = mat_func(self.transform_amt, 4, self.axis_as_vector)
        self.obj.matrix_world = transform_matrix

    def scale_object(self):
        if self.axis == "ALL":
            scale_attr = getattr(self.obj, "scale")
            scale_attr *= self.transform_amt
        else:
            scale_attr = getattr(self.obj.scale, self.axis.lower())
            new_val = scale_attr * self.transform_amt
            setattr(self.obj.scale, self.axis.lower(), new_val)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        if event.ctrl:
            self.transform_amt *= -1
        if event.alt:
            self.transform_amt = 1 / self.transform_amt
        return self.execute(context)

    def execute(self, context):
        self.obj = self.get_active_obj()
        self.mx = self.obj.matrix_world
        scale_apply = False
        rotation_apply = False
        if self.transform_type == "Rotation":
            rotation_apply = True
            self.rotate_object()
        else:
            scale_apply = True
            self.scale_object()
        bpy.ops.object.transform_apply(
            location=False, rotation=rotation_apply, scale=scale_apply
        )
        return {"FINISHED"}


class DuplicateObjectDeleter(OperatorBaseClass):
    def __init__(self, context, args, op):
        super().__init__(context, args, op=op)
        self.ids = []
        self.all_objs = []
        self.dupe_objs = []
        self.good_objs = []
        self.deps = self.context.evaluated_depsgraph_get()

    def _has_same_verts(self, obj, dupe):
        print("comparing objs: ", obj.name, dupe.name)
        obj = obj.evaluated_get(self.deps)
        dupe = dupe.evaluated_get(self.deps)
        same_verts = len(dupe.data.vertices[:]) == len(obj.data.vertices[:])
        print("Has same verts: ", same_verts)
        return same_verts

    def get_obj_name(self, obj):
        return re.split("\.|(_)\d{2}", obj.name)[0]

    def get_obj_id(self, obj):
        loc = obj.location
        name = self.get_obj_name(obj)
        return (loc, name)

    def delete_dupe_objects(self):
        sel_objs = self.context.selected_objects[:]
        for obj in sel_objs:
            if obj.type == "MESH":
                self.all_objs.append(obj)
        duped_objs = []
        for obj in sel_objs:
            if obj.type == "MESH":
                id1 = self.get_obj_id(obj)
                for check_obj in self.all_objs[:]:
                    if check_obj != obj:
                        id2 = self.get_obj_id(check_obj)
                        if (
                            id1 == id2
                            and self._has_same_verts(obj, check_obj)
                            and check_obj not in self.good_objs
                        ):
                            duped_objs.append(check_obj)
                        else:
                            self.good_objs.append(obj)

        self.op.report({"INFO"}, f"Finished. {len(duped_objs)} deleted.")
        for del_obj in duped_objs[:]:
            try:
                bpy.data.objects.remove(del_obj)
            except ReferenceError:
                print(f"couldn't delete: {del_obj.name}")
        return {"FINISHED"}


class OBJECT_OT_RemoveDoubledObjects(Operator):
    bl_idname = "object.remove_doubled_objects"
    bl_label = "Remove Doubled Objects"
    desc_lines = [
        "Loop over selected objects and delete objects",
        "that share the same location and name w/o suffix.",
    ]
    bl_description = "\n".join(desc_lines)
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 1

    def execute(self, context):
        args = self.as_keywords()
        dod = DuplicateObjectDeleter(context, args, op=self)
        return dod.delete_dupe_objects()


class OBJECT_OT_deselect_parented_objs(CustomOperator, Operator):
    bl_idname = "object.deselect_parented_objs"
    bl_label = "Deselect Parented Objs"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        objs = context.selected_objects
        for obj in objs[:]:
            if obj.parent:
                obj.select_set(False)
        return {"FINISHED"}


class OBJECT_OT_quick_cloth_pin(CustomBmeshOperator, Operator):
    bl_idname = "object.quick_cloth_pin"
    bl_label = "Quick Cloth Pin"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.obj = self.get_active_obj()
        self.mesh = self.obj.data
        self.verts = self.mesh.vertices
        self.locs = [vert.co.z for vert in self.verts[:]]
        max_z = max(self.locs)
        self.max_z_vert_data = []
        for vert in self.verts[:]:
            delta = abs(max_z - vert.co.z)
            print(delta)
            if delta < 0.01:
                self.max_z_vert_data.append(vert.index)
        if "pin" not in [group.name for group in self.obj.vertex_groups[:]]:
            group = self.obj.vertex_groups.new(name="pin")
        else:
            group = self.obj.vertex_groups["pin"]
        group.add(self.max_z_vert_data, 1.0, "ADD")

        for mod in self.obj.modifiers[:]:
            if mod.type == "CLOTH":
                mod.settings.vertex_group_mass = "pin"
        return {"FINISHED"}


def toggle_multires(context, args):
    highest = args.pop("highest")

    for obj in context.selected_objects[:]:
        if obj.type == "MESH":
            for mod in obj.modifiers[:]:
                if mod.type == "MULTIRES":
                    if highest:
                        mod.levels = mod.total_levels
                    else:
                        mod.levels = 0


class OBJECT_OT_toggle_multires(CustomBmeshOperator, Operator):
    bl_idname = "object.toggle_multires"
    bl_label = "Toggle Multires"
    bl_options = {"REGISTER", "UNDO"}

    highest: bpy.props.BoolProperty(name="All to Highest", default=False)

    def execute(self, context):
        args = self.as_keywords()
        toggle_multires(context, args)
        return {"FINISHED"}


def deselect_parented_objs_menu_func(self, context):
    layout = self.layout
    layout.operator("object.deselect_parented_objs")


def hide_widget_objects_menu_func(self, context):
    layout = self.layout
    layout.operator("object.move_widgets_to_collection")


def deselect_modifier_panel_ops(self, context):
    layout = self.layout
    col = layout.column(align=True)
    row = col.row(align=True)
    row.operator("object.toggle_subdiv_vis")
    row.operator("object.toggle_mirror_clipping")
    row = col.row(align=True)
    op = row.operator(
        "object.toggle_multires",
        text="Multires to Lowest",
    )
    op.highest = False
    op = row.operator("object.toggle_multires", text="Multires to Highest")
    op.highest = True


def is_widget(obj):
    return obj.type == "MESH" and "WGT" in obj.name


def create_wgt_collection():
    coll_exists = False
    try:
        coll = bpy.data.collections["wgts"]
    except KeyError:
        coll = bpy.data.collections.new("wgts")
    return coll


def coll_index():
    for i, coll in enumerate(bpy.data.collections[:]):
        print(i, coll)
        if coll.name == "wgts":
            return i


def move_objects(context):
    coll = create_wgt_collection()
    for obj in bpy.data.objects[:]:
        if is_widget(obj):
            user_col = obj.users_collection[0]
            user_col.objects.unlink(obj)
            coll.objects.link(obj)

    coll.hide_viewport = True


class OBJECT_OT_move_wgts_to_collection(bpy.types.Operator):
    bl_idname = "object.move_widgets_to_collection"
    bl_label = "Hide WGT Objects"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        move_objects(context)
        return {"FINISHED"}


class OBJECT_OT_clean_up_quadremesh_names(bpy.types.Operator):
    bl_idname = "object.clean_up_quadremesh_names"
    bl_label = "Clean Up QuadRemesh Names"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for obj in bpy.data.objects[:]:
            obj.name = obj.name.replace("Retopo_", "")
        return {"FINISHED"}


def generate_random_v_colors_per_obj(context, **args):
    multi_obj = args.pop("multi_obj")
    color_picker = args.pop("color_picker")
    objs = context.selected_objects[:]
    colors = []
    margin = 0.03

    def generate_color():
        too_close = False
        color = np.random.random_sample((3,))
        color = np.append(color, 1.0)
        for col in colors:
            col_avg = np.mean(col)
            new_col_avg = np.mean(color)
            diff = col_avg - new_col_avg
            if abs(diff) < margin:
                too_close = True
        if not too_close:
            colors.append(color)
            return color
        return generate_color()

    if color_picker:
        color = context.scene.mpm_props.custom_vertex_color
    elif not multi_obj:
        color = generate_color()

    for obj in objs:
        if obj.type == "MESH":
            mesh = obj.data
            vcol = mesh.vertex_colors
            color_layer = vcol["Col"] if vcol else vcol.new()
            if multi_obj:
                color = generate_color()
            i = 0
            for poly in mesh.polygons[:]:
                for loop in poly.loop_indices:
                    color_layer.data[i].color = color
                    i += 1


def move_bool_objects(context):
    bool_coll = utils.get_or_create_collection("bools")
    for obj in context.selected_objects:
        coll = utils.find_objects_collection(obj)
        if obj.display_type == "BOUNDS":
            coll.objects.unlink(obj)
            bool_coll.objects.link(obj)


class OBJECT_OT_move_bool_objs_to_coll(bpy.types.Operator):
    bl_idname = "object.move_bool_objects_to_coll"
    bl_label = "Move Bool Objects"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.selected_objects

    def execute(self, context):
        move_bool_objects(context)
        return {"FINISHED"}


class OBJECT_OT_generate_random_v_colors_per_obj(bpy.types.Operator):
    bl_idname = "object.generate_random_v_colors_per_obj"
    bl_label = "Random Vertex Color Per Object"
    bl_options = {"REGISTER", "UNDO"}

    multi_obj: bpy.props.BoolProperty(
        default=False,
        name="Multi Object",
        description="multi_obj: True, Give each selected object it's own random color. False: Set all objects to one color",
    )
    color_picker: bpy.props.BoolProperty(
        default=False,
        name="Color Picker",
        description="If true, use color picker to assign vertex_color.",
    )

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.selected_objects

    def execute(self, context):
        args = self.as_keywords()
        generate_random_v_colors_per_obj(context, **args)
        return {"FINISHED"}


def add_custom_light(context, args):
    light_type = args.pop("light_type")
    light_name = light_type.capitalize()
    cursor_loc = context.scene.cursor.location
    light_data = bpy.data.lights.new(light_name, type=light_type)
    light_data.use_contact_shadow = True
    light_obj = bpy.data.objects.new(light_name, light_data)
    context.collection.objects.link(light_obj)
    light_obj.location = cursor_loc
    context.view_layer.objects.active = light_obj
    light_obj.select_set(True)


class OBJECT_custom_light_add(bpy.types.Operator):
    bl_idname = "object.custom_light_add"
    bl_label = "Custom Add Light"
    bl_options = {"REGISTER", "UNDO"}

    light_type: bpy.props.EnumProperty(
        items={
            ("AREA", "Area", "Area"),
            ("POINT", "Point", "Point"),
            ("SPOT", "Spot", "Spot"),
            ("SUN", "Sun", "Sun"),
        },
        name="Light Type",
    )

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        args = self.as_keywords()
        add_custom_light(context, args)
        return {"FINISHED"}


def get_mesh_vcol_layer(mesh):
    vcol = mesh.vertex_colors
    color_layer = vcol["Col"] if vcol else vcol.new()
    return color_layer


def get_active_obj_vcol(obj):
    mesh = obj.data
    color_layer = get_mesh_vcol_layer(mesh)
    rgb_values = []
    i = 0
    for poly in mesh.polygons[:]:
        for loop in poly.loop_indices:
            rgb_val = color_layer.data[i].color[:]
            rgb_values.append(np.array(rgb_val))
            i += 1

    return np.mean(rgb_values, axis=0)


def copy_vcol_from_active(context):
    objs = context.selected_objects
    active_obj = context.active_object
    active_vcol = get_active_obj_vcol(active_obj)
    for obj in objs:
        if obj.type == "MESH" and obj != active_obj:
            mesh = obj.data
            color_layer = get_mesh_vcol_layer(mesh)
            i = 0
            for poly in mesh.polygons[:]:
                for loop in poly.loop_indices:
                    color_layer.data[i].color = active_vcol
                    i += 1


class OBJECT_OT_CopyVcolFromActive(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "object.copy_vcol_from_active"
    bl_label = "Copy Vertex Color from Active"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None and len(context.selected_objects[:]) > 1
        )

    def execute(self, context):
        copy_vcol_from_active(context)
        return {"FINISHED"}


def copy_obj_name(context):
    for obj in bpy.context.selected_objects[:]:
        active_obj = bpy.context.view_layer.objects.active
        if obj != active_obj:
            obj.name = active_obj.name


class OBJECT_OT_CopyObjName(bpy.types.Operator):
    bl_idname = "object.copy_obj_name"
    bl_label = "Copy Object Name"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        copy_obj_name(context)
        return {"FINISHED"}

class SMObjectNamer(OperatorBaseClass):
    def __init__(self, context, args=None, op=None, index=None, root_obj=None):
        super().__init__(context, args=args, op=op)
        self.index = index
        self.parent = root_obj

    @staticmethod
    def _get_num_suffix(index):
        return str(index + 1).zfill(2)

    @property
    def _child_objects(self):
        return [obj for obj in self.parent.children_recursive]

    def get_name(self, obj, index):
        if obj == self.parent:
            name = self.name_str
        else:
            name = f"{self.name_str}_{self._get_num_suffix(self.index)}_SubObj"
        return index, name

    def format_name(self, i, name):
        prefix = "SM"
        suffix = self._get_num_suffix(i)
        return "_".join([prefix, name, suffix])

    def rename_objs(self):
        i, name = self.get_name(self.parent, self.index)
        self.parent.name = self.format_name(i, name)
        for i, obj in enumerate(self._child_objects[:]):
            _, name = self.get_name(obj, i)
            obj.name = self.format_name(i, name)


class OBJECT_OT_NameStaticMeshGrouping(bpy.types.Operator):
    bl_idname = "object.name_static_mesh_grouping"
    bl_label = "Name Static Mesh Grouping"
    bl_options = {"REGISTER", "UNDO"}

    name_str: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        objs = context.selected_objects[:]
        for i, obj in enumerate(objs):
            args = self.as_keywords()
            SMNamer = SMObjectNamer(context, args=args, op=self, index=i, root_obj=obj)
            SMNamer.rename_objs()
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        # Edit first editable button in popup
        def row_with_icon(layout, icon):
            row = layout.row()
            row.activate_init = True
            row.label(icon=icon)
            return row

        mode = context.mode
        row = row_with_icon(layout, "OBJECT_DATAMODE")
        row.prop(self, "name_str")

class OBJECT_OT_CustomConvertObject(Operator):
    """Convert object to another object type. CTRL > Keep Original"""

    bl_idname = "object.custom_convert_object"
    bl_label = "Custom Convert Object"
    bl_description = """Convert object to another object type. CTRL > Keep Original."""
    bl_options = {"REGISTER", "UNDO"}

    target: bpy.props.StringProperty(default="MESH", name="Target")
    keep_original: bpy.props.BoolProperty(default=False, name="Keep Original")


    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def invoke(self, context, event):
        self.keep_original = False
        if event.ctrl:
            self.keep_original = True 
        return self.execute(context)
    
    def execute(self, context):
        bpy.ops.object.convert(target=self.target, keep_original=self.keep_original)
        return {"FINISHED"}



classes = (
    AddCameraCustom,
    AddLightSetup,
    SetCustomBatchName,
    # delete later
    JG_SetUVChannels,
    OBJECT_OT_sort_items_on_axis,
    OBJECT_OT_align_objects,
    OBJECT_OT_set_auto_smooth_modal,
    OBJECT_add_empty_at_objs_center,
    OBJECT_OT_quick_transforms,
    OBJECT_OT_RemoveDoubledObjects,
    OBJECT_OT_deselect_parented_objs,
    OBJECT_OT_quick_cloth_pin,
    OBJECT_OT_toggle_multires,
    OBJECT_OT_move_wgts_to_collection,
    OBJECT_OT_clean_up_quadremesh_names,
    OBJECT_OT_generate_random_v_colors_per_obj,
    OBJECT_OT_CopyVcolFromActive,
    OBJECT_custom_light_add,
    OBJECT_OT_CopyObjName,
    OBJECT_OT_NameStaticMeshGrouping,
    OBJECT_OT_CustomConvertObject,
)


kms = [
    {
        "keymap_operator": OBJECT_OT_set_auto_smooth_modal.bl_idname,
        "name": "Object Mode",
        "letter": "H",
        "shift": 0,
        "ctrl": 1,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {},
    },
    {
        "keymap_operator": OBJECT_OT_align_objects.bl_idname,
        "name": "Object Mode",
        "letter": "X",
        "shift": 0,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {},
    },
    {
        "keymap_operator": OBJECT_OT_sort_items_on_axis.bl_idname,
        "name": "Object Mode",
        "letter": "O",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {},
    },
]

addon_keymaps = []


def register():
    utils.register_classes(classes)
    utils.register_keymaps(kms, addon_keymaps)
    bpy.types.VIEW3D_MT_select_object.append(deselect_parented_objs_menu_func)
    bpy.types.VIEW3D_MT_object.append(hide_widget_objects_menu_func)
    bpy.types.DATA_PT_modifiers.prepend(deselect_modifier_panel_ops)


def unregister():
    bpy.types.VIEW3D_MT_select_object.remove(deselect_parented_objs_menu_func)
    bpy.types.DATA_PT_modifiers.remove(deselect_modifier_panel_ops)
    bpy.types.DATA_PT_modifiers.remove(deselect_modifier_panel_ops)

    for cls in classes:
        bpy.utils.unregister_class(cls)
        utils.unregister_keymaps(kms)
