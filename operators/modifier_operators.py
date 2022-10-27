from collections import deque
from statistics import mean

import numpy as np
import bpy
from bpy.types import Operator
import bmesh
from mathutils import Vector
from .custom_operator import CustomOperator, CustomModalOperator, ModalDrawText
from my_pie_menus.resources import utils


class CustomAddMirrorModifier(CustomOperator, Operator):
    """Add Mirror Custom Modifier"""

    bl_idname = "object.custom_mirror_modifier"
    bl_label = "Add Custom Mirror"
    bl_options = {"REGISTER", "UNDO"}

    mirror_type: bpy.props.StringProperty(
        default="",
    )
    mirror_direction: bpy.props.StringProperty(
        default="",
    )
    bisect: bpy.props.BoolProperty(default=True)
    bisect_only: bpy.props.BoolProperty(default=False)

    multi_object = False

    def invoke(self, context, event):
        self.bisect_only = False
        if event.alt:
            self.bisect = False
        if event.ctrl:
            self.bisect_only = True

        return self.execute(context)

    def add_mirror_mod(self, obj):
        if self.bisect and not self.multi_object:
            self._bisect_mesh()
        if not self.bisect_only:
            bpy.ops.object.modifier_add(type='MIRROR')
            axis_index = self.mirror_axis
            mirror_mod = obj.modifiers[:][-1]
            for i in range(3):
                mirror_mod.use_axis[i] = False
                mirror_mod.use_bisect_axis[i] = False
            mirror_mod.use_axis[axis_index] = True
            mirror_mod.use_bisect_axis[axis_index] = True
            mirror_mod.use_mirror_u = True
            mirror_mod.use_clip = True
            if self.multi_object:
                mirror_mod.mirror_object = self.mirror_obj
            if self.mirror_type not in {
                "Z_POS",
                "X_POS",
                "Y_POS",
            }:
                mirror_mod.use_bisect_flip_axis[axis_index] = True

    def execute(self, context):
        in_edit_mode = bool(bpy.context.object.mode == "EDIT")
        if in_edit_mode:
            bpy.ops.object.mode_set(mode="OBJECT")
        if len(context.selected_objects) > 1:
            self.multi_object = True
            objs = set(context.selected_objects)
            mirror_obj = set([context.active_object])
            objs = objs - mirror_obj
            self.mirror_obj = self.get_active_obj()
            for obj in objs:
                context.view_layer.objects.active = obj
                self.add_mirror_mod(obj)
        else:
            obj = self.get_active_obj()
            self.add_mirror_mod(obj)
        if in_edit_mode:
            bpy.ops.object.mode_set(mode="EDIT")
        return {'FINISHED'}

    def _bisect_mesh(self):
        C = bpy.context
        obj = C.active_object
        bm = bmesh.new()
        me = obj.data
        bm.from_mesh(me)

        def get_geom(bm):
            geom = []
            geom.extend(bm.verts[:])
            geom.extend(bm.edges[:])
            geom.extend(bm.faces[:])
            return geom

        kwargs = self.bisect_args

        ret = bmesh.ops.bisect_plane(
            bm,
            geom=get_geom(bm),
            dist=0.0001,
            plane_co=(0, 0, 0),
            **kwargs,
        )

        bm.to_mesh(me)
        me.update()

    @property
    def mirror_axis(self):
        if self.mirror_type:
            if "X" in self.mirror_type:
                return 0
            elif "Y" in self.mirror_type:
                return 1
            return 2

    @property
    def bisect_args(self):
        if self.mirror_type:
            vals = {
                'X_NEG': {
                    'plane_no': (1, 0, 0),
                    'clear_inner': False,
                    'clear_outer': True,
                },
                'Y_NEG': {
                    'plane_no': (0, 1, 0),
                    'clear_inner': False,
                    'clear_outer': True,
                },
                'Z_NEG': {
                    'plane_no': (0, 0, 1),
                    'clear_inner': False,
                    'clear_outer': True,
                },
                'X_POS': {
                    'plane_no': (1, 0, 0),
                    'clear_inner': True,
                    'clear_outer': False,
                },
                'Y_POS': {
                    'plane_no': (0, 1, 0),
                    'clear_inner': True,
                    'clear_outer': False,
                },
                'Z_POS': {
                    'plane_no': (0, 0, 1),
                    'clear_inner': True,
                    'clear_outer': False,
                },
            }

            return vals[self.mirror_type]


class BevelModifier(CustomOperator):

    bl_options = {'REGISTER', "UNDO"}

    limit_method: bpy.props.EnumProperty(
        items=(
            ('WEIGHT', "Weight", "Weight"),
            ('ANGLE', "Angle", "Weight"),
        ),
        name='Weight',
        description='Weighted Limit Method',
        default="ANGLE",
    )

    def _next_limit_method(self, event):
        methods = [
            'WEIGHT',
            'ANGLE',
        ]
        addend = 1
        if event.shift:
            addend = -1
        curr_index = methods.index(self.limit_method)
        new_index = (curr_index + addend) % len(methods)
        return methods[new_index]

    @property
    def relative_bwidth(self):
        obj = self.get_active_obj()
        return mean(obj.dimensions) / 65

    def _add_bevel_modifier(self, harden_normals=True, profile=0.5, angle_limit=45):
        in_edit_mode = bool(bpy.context.object.mode == "EDIT")
        if in_edit_mode:
            bpy.ops.object.mode_set(mode="OBJECT")
        obj = self.get_active_obj()
        bpy.ops.object.shade_smooth()
        obj.data.use_auto_smooth = True
        bpy.ops.object.modifier_add(type='BEVEL')
        bevel_mod = obj.modifiers[:][-1]
        bevel_mod.limit_method = self.limit_method
        bevel_mod.segments = 2
        bevel_mod.width = self.relative_bwidth
        bevel_mod.profile = profile
        bevel_mod.angle_limit = np.radians(angle_limit)
        bevel_mod.harden_normals = harden_normals
        bevel_mod.miter_outer = "MITER_ARC"
        bevel_mod.use_clamp_overlap = False
        self.bevel_mod = bevel_mod
        if in_edit_mode:
            bpy.ops.object.mode_set(mode="EDIT")


class CustomAddBevelModifier(BevelModifier, CustomModalOperator, Operator):
    """Add Custom Bevel Modifier"""

    bl_idname = "object.custom_bevel_modifier"
    bl_label = "Add Custom Bevel"
    bl_parent_id = "CustomOperator"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add Bevel modifier, Angle is default limit method, Hold ALT for Weighted."

    @property
    def modal_info_string(self):
        lines = [
            f"BEVEL WIDTH: {self.bevel_mod.width:.3f}",
            f"SEGMENTS (MouseWheel): {self.bevel_mod.segments}",
            f"LIMIT METHOD (Tab): {self.limit_method}",
            f"CLAMP OVERLAP (C): {self.bevel_mod.use_clamp_overlap}",
            f"HARDEN NORMALS (H): {self.bevel_mod.harden_normals}",
        ]
        return ", ".join(lines)

    def invoke(self, context, event):
        if event.alt:
            self.limit_method = "WEIGHT"
        self._add_bevel_modifier()
        self.init_mouse_x = event.mouse_x
        self.bwidth = self.relative_bwidth
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        self.display_modal_info(self.modal_info_string, context)
        self.multiplier = 0.001
        if event.shift:
            self.multiplier = 0.0001
        if event.type == "MOUSEMOVE":

            delta = (self.init_mouse_x - event.mouse_x) * self.multiplier
            self.bevel_mod.width -= delta
            self.init_mouse_x = event.mouse_x
        elif event.type == "WHEELUPMOUSE":
            self.bevel_mod.segments += 1
        elif event.type == "WHEELDOWNMOUSE":
            self.bevel_mod.segments -= 1
        elif event.value == "PRESS":
            if event.type == "TAB":
                new_lm = self._next_limit_method(event)
                self.bevel_mod.limit_method = new_lm
            elif event.type == "C":
                col = self.bevel_mod.use_clamp_overlap
                self.bevel_mod.use_clamp_overlap = not col
            elif event.type == "H":
                hn = self.bevel_mod.harden_normals
                self.bevel_mod.harden_normals = not hn
        elif event.type in {"ESC", "RIGHTMOUSE"}:
            bpy.ops.object.modifier_remove(modifier=self.bevel_mod.name)
            return self.exit_modal(context, cancelled=True)
        elif event.type == "LEFTMOUSE":
            return self.exit_modal(context)
        return {"RUNNING_MODAL"}


def apply_relevant_mods(obj):
    relevant_mods = [
        "SOLIDIFY",
    ]
    for mod in obj.modifiers[:]:
        if mod.type in relevant_mods:
            bpy.ops.object.modifier_apply(modifier=mod.name)


def set_angle(edge, sharpness, creases):
    try:
        angle = edge.calc_face_angle()
    except ValueError:
        angle = 0.0
    print("ANGLE: ", angle)

    delta = angle - np.radians(sharpness)
    print("DELTA: ", delta)
    if delta >= 0.001:
        edge[creases] = 1.0
    else:
        edge[creases] = 0.0
    print("CREASE_AMT: ", edge[creases])


def auto_crease_subdivide(context, args):
    sharpness = args.pop('sharpness')
    in_edit = "EDIT" in context.mode
    if in_edit:
        bpy.ops.object.mode_set(mode="OBJECT")
    for obj in context.selected_objects:
        if obj.type == "MESH":
            context.view_layer.objects.active = obj
            apply_relevant_mods(obj)
            me = obj.data
            bm = bmesh.new()
            bm.from_mesh(me)

            creases = bm.edges.layers.crease.verify()

            for edge in bm.edges[:]:
                set_angle(edge, sharpness, creases)
            bm.to_mesh(me)
            bpy.ops.object.modifier_add(type="SUBSURF")
            bm.free()
    if in_edit:
        bpy.ops.object.mode_set(mode="EDIT")


class OBJECT_OT_auto_crease_subdivide(bpy.types.Operator):
    """Automatically set sharp edges to creased and adds a subsurf mod. Will apply Solidify modifiers."""

    bl_idname = "object.auto_crease_subdivide"
    bl_label = "Simple Object Operator"

    sharpness: bpy.props.FloatProperty(name="Sharpness", description="Degree to set sharp angles at.", default=45.0)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        args = self.as_keywords()
        auto_crease_subdivide(context, args)
        return {'FINISHED'}


class CustomAddQuickBevSubSurfModifier(BevelModifier, Operator):
    """Add Custom Bevel Modifier with Subsurf"""

    bl_idname = "object.custom_bevel_subsurf_modifier"
    bl_label = "Add Custom Bevel Subsurf"
    bl_parent_id = "CustomAddBevelModifier"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = self.get_active_obj()
        in_edit = "EDIT" in context.mode
        if in_edit:
            bpy.ops.object.mode_set(mode="OBJECT")
        self._add_bevel_modifier()
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.ops.object.modifier_add(type='WEIGHTED_NORMAL')
        bpy.ops.object.shade_smooth()
        obj.data.use_auto_smooth = True
        self.close_modifiers()
        if in_edit:
            bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


class CustomWeightedNormal(CustomOperator, Operator):
    """Add Custom Weighted Normal Modifier"""

    bl_idname = "object.custom_weighted_normal"
    bl_label = "Add Custom Weighted Normal"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type in {"MESH"}

    def execute(self, context):
        obj = self.get_active_obj()
        obj.data.use_auto_smooth = True
        bpy.ops.object.modifier_add(type="WEIGHTED_NORMAL")
        self.close_modifiers()

        return {"FINISHED"}


class CustomSimpleDeform(CustomModalOperator, Operator):
    """Add Custom Simple Deform Modifier"""

    bl_idname = "object.custom_simple_deform"
    bl_label = "Add Custom Simple Deform"
    bl_options = {"REGISTER", "UNDO"}

    angle: bpy.props.FloatProperty(name='angle', description='Deform Angle', default=45.0)
    axis: bpy.props.StringProperty(name='axis', description='Deform Axis', default="Z")
    x: bpy.props.IntProperty(min=0, max=360)
    mod = None

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type in {"MESH", "CURVE"}

    def invoke(self, context, event):
        obj = self.get_active_obj()
        bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
        self.mod = self._get_last_modifier()
        self.mod.deform_method = 'BEND'
        self.mod.deform_axis = 'Z'
        self.init_x = event.mouse_x
        self.x = 0
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        msg = f'Angle: {self.angle}, Axis: {self.axis}'
        self.display_modal_info(msg, context)
        if event.type == 'MOUSEMOVE':
            delta = int((event.mouse_x) - self.init_x)
            self.angle = utils.clamp(delta, 0, 360)
            self.mod.angle = np.radians(self.angle)
        elif event.type in {"X", "Y", "Z"}:
            self.axis = event.type
            self.mod.deform_axis = self.axis

        elif event.type == 'LEFTMOUSE':  # Confirm
            self._clear_info(context)
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            self._clear_info(context)
            bpy.ops.object.modifier_remove(modifier=self.mod.name)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


class CustomShrinkwrap(CustomOperator, Operator):
    """Add Custom Shrinkwrap Modifier"""

    bl_options = {"REGISTER", "UNDO"}

    bl_idname = "object.custom_shrinkwrap"
    bl_label = "Add Custom Shrinkwrap"

    apply_projection = False

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type in {"MESH", "CURVE"}

    def invoke(self, context, event):
        if event.alt:
            self.apply_projection = True
        return self.execute(context)

    def execute(self, context):
        num_objs = len(bpy.context.selected_objects)
        if num_objs < 2:
            bpy.ops.object.modifier_add(type="SHRINKWRAP")
            self.apply_projection = False
        else:
            mod, target = self.get_mod_and_target_objects()
            bpy.context.view_layer.objects.active = mod
            bpy.ops.object.modifier_add(type="SHRINKWRAP")
        sw = self._get_last_modifier()
        sw.target = target
        sw.wrap_mode = "ABOVE_SURFACE"
        sw.show_on_cage = True
        sw.offset = 0.0001
        if self.apply_projection:
            for mod in mod.modifiers[:]:
                if mod.type in {"SUBSURF", "SHRINKWRAP"}:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
        return {"FINISHED"}


# class CustomLattice(CustomOperator, Operator):
#     """Add Custom Lattice Modifier"""

#     bl_idname = "object.custom_lattice"
#     bl_label = "Add Custom Lattice"
#     bl_options = {"REGISTER", "UNDO"}

#     def execute(self, context):
#         bpy.ops.object.modifier_add(type="LATTICE")
#         lat = self._get_last_modifier()
#         bpy.ops.object.smart_add_lattice()
#         obj = self.get_active_obj()
#         lat.object = obj
#         return {"FINISHED"}


class CustomRemesh(CustomOperator, Operator):
    """Add Custom Remesh Modifier"""

    bl_idname = "object.custom_remesh"
    bl_label = "Add Custom Remesh"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type in {"MESH", "CURVE"}

    def execute(self, context):
        bpy.ops.object.modifier_add(type="REMESH")
        mod = self._get_last_modifier()
        mod.voxel_size = 0.025
        mod.use_smooth_shade = True
        return {"FINISHED"}


class CustomDecimate(CustomOperator, Operator):
    """Add Custom Decimate Modifier"""

    bl_options = {"REGISTER", "UNDO"}

    bl_idname = "object.custom_decimate"
    bl_label = "Add Custom Decimate"

    apply_mod = False
    mode = None

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type in {"MESH", "CURVE"}

    def invoke(self, context, event):
        self.mode = self.get_current_mode(context)
        if event.alt:
            self.apply_mod = True
        return self.execute(context)

    def execute(self, context):
        switch_mode = self.mode in {"EDIT", "SCULPT"}
        if switch_mode:
            self.to_mode("OBJECT")
        bpy.ops.object.modifier_add(type="DECIMATE")
        mod = self._get_last_modifier()
        mod.ratio = 0.2
        if self.apply_mod:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        if switch_mode:
            self.to_mode(self.mode)
        return {"FINISHED"}


class ArrayModalOperator(CustomModalOperator, Operator):
    """Move an object with the mouse, example"""

    bl_idname = "object.array_modal"
    bl_label = "Array Modal"
    constant: bpy.props.BoolProperty(default=True)
    relative: bpy.props.BoolProperty(default=False)
    offset: bpy.props.FloatProperty(default=0.0)
    count: bpy.props.IntProperty()
    working_axes = {"X": True, "Y": False, "Z": False}

    @property
    def current_axes(self):
        return [ax for ax, val in self.working_axes.items() if val]

    @property
    def array(self):
        obj = self.get_active_obj()
        return obj.modifiers[self.mod_name]

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type in {"MESH", "CURVE"}

    def _set_axis_values(self, axes: list, value, single=True):
        array_axes = ['X', 'Y', 'Z']
        if single:
            self._set_axis_values(array_axes, 0, single=False)
        for a in axes:
            index = array_axes.index(a)
            if self.constant:
                self.modifier.constant_offset_displace[index] = value
            else:
                self.modifier.relative_offset_displace[index] = value

    def _set_array_count(self, event_type):
        value = 1
        if event_type == 'WHEELDOWNMOUSE':
            value = -1
        self.modifier.count += value

    def _report_modal_status(self, context):
        type = "CONSTANT"
        if self.relative:
            type = "RELATIVE"
        msg = [
            f'COUNT: {self.modifier.count}',
            f'OFFSET: {self.offset:.2f}',
            f'AXIS: {",".join(self.current_axes)}',
            f'TYPE: {type}',
        ]
        context.area.header_text_set(' '.join(msg))

    def modal(self, context, event):
        self._report_modal_status(context)
        # handle axis changing
        if event.type in {'X', "Y", "Z"}:
            if event.value == 'PRESS':
                ax = event.type
                # if pressing shift, XYZ will add or remove
                # itself from active axes
                if event.shift:
                    cur_val = self.working_axes[ax]
                    self.working_axes[ax] = not cur_val
                # otherwise toggle axes individually
                else:
                    for axis, value in self.working_axes.items():
                        self.working_axes[axis] = False
                    self.working_axes[ax] = True
        if event.type == "MIDDLEMOUSE":
            return {'PASS_THROUGH'}

        if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            self._set_array_count(event.type)

        if event.type == "TAB":
            if event.value == "PRESS":
                self.constant = not self.constant
                self.relative = not self.relative

        if event.type == 'MOUSEMOVE':
            multiplier = 0.1
            if event.shift:
                multiplier = 0.01
            delta = self.initial_mouse - event.mouse_x
            if event.ctrl:
                snap_val = np.floor(delta * (-multiplier)) + 1
                self.offset = snap_val
            else:
                self.offset = delta * (-multiplier)
            self.modifier.use_constant_offset = self.constant
            self.modifier.use_relative_offset = self.relative
            self._set_axis_values(self.current_axes, self.offset)

        elif event.type == 'LEFTMOUSE':
            self._clear_info(context)
            self.close_modifiers()
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self._clear_info(context)
            bpy.ops.object.modifier_remove(modifier=self.modifier.name)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        obj = self.get_active_obj()
        bpy.ops.object.modifier_add(type="ARRAY")
        array = self._get_last_modifier()
        array.use_constant_offset = True
        array.use_relative_offset = False
        self.mod_name = array.name
        self._set_axis_values(self.current_axes, self.offset)

        if context.object:
            self.initial_mouse = event.mouse_x
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}


class SolidifyModalOperator(CustomModalOperator, Operator):
    bl_idname = "object.solidify_modal"
    bl_label = "Solidify Modal"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type in {"MESH", "CURVE"}

    thickness: bpy.props.FloatProperty()

    def modal(self, context, event):
        msg = f"Thickness: {self.thickness}"
        if self.numpad_value:
            msg += f" Value: {self.string_numpad_value}"
        context.area.header_text_set(msg)
        if event.type == 'MOUSEMOVE':
            multiplier = 0.01
            if event.shift:
                multiplier = 0.001
            self.thickness = self._initial_mouse - event.mouse_x
            self.modifier.thickness = (self.thickness * multiplier) * -1

        if event.type == 'F':
            if event.value == "PRESS":
                self.modifier.offset *= -1

        if event.type in self.numpad_input:
            if event.value == "PRESS":
                if event.type == "NUMPAD_ENTER":
                    self.modifier.thickness = self.float_numpad_value
                    return self.exit_modal(context)
                if event.type == "BACK_SPACE":
                    self.numpad_value.pop()
                else:
                    value = event.unicode
                    self.numpad_value.append(value)

        elif event.type == 'LEFTMOUSE':
            return self.exit_modal(context)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return self.exit_modal(context, cancelled=True)

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            obj = self.get_active_obj()
            bpy.ops.object.modifier_add(type="SOLIDIFY")
            mod = self._get_last_modifier()
            mod.use_even_offset = True
            mod.offset = 1
            mod.use_quality_normals = True
            mod.solidify_mode = "NON_MANIFOLD"
            self.mod_name = mod.name
            self.thickness = mod.thickness

            self._initial_mouse = event.mouse_x
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}


class ScrewModalOperator(CustomModalOperator, Operator):
    bl_idname = "object.screw_modal"
    bl_label = "Screw Modal"

    mod_name: bpy.props.StringProperty()
    screw_offset: bpy.props.FloatProperty()
    angle: bpy.props.FloatProperty()
    steps: bpy.props.IntProperty()
    initial_mouse: bpy.props.FloatProperty()
    iterations: bpy.props.IntProperty()
    axis: bpy.props.StringProperty()
    use_object_screw_offset: bpy.props.BoolProperty()
    use_normal_calculate: bpy.props.BoolProperty()
    use_normal_flip: bpy.props.BoolProperty()

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type in {"MESH", "CURVE"}

    def set_screw_angle(self, delta, multiplier):
        angle = delta * multiplier
        new_angle = self.modifier.angle - np.radians(angle)
        self.modifier.angle = utils.clamp(new_angle, 0, 2 * np.pi)

    def set_screw_count(self, event_type):
        if event_type == "WHEELUPMOUSE":
            self.modifier.steps += 1
        else:
            self.modifier.steps -= 1

    def _log_info_msg(self):
        mod = self.modifier
        msg = [
            f"Degrees: {np.degrees(mod.angle)}",
            f"Steps: {mod.steps}",
            f"Offset: {mod.screw_offset}",
            f"Iterations: {mod.iterations}",
            f"Screw Axis: {mod.axis}",
        ]
        return ', '.join(msg)

    def modal(self, context, event):
        self.display_modal_info(self._log_info_msg(), context)
        if event.type == 'MOUSEMOVE':
            multiplier = 0.1
            if event.shift:
                multiplier = 0.01
            delta = self.initial_mouse - event.mouse_x
            self.set_screw_angle(delta, multiplier)

        if event.type in self.wheel_input:
            self.set_screw_count(event.type)

        if event.type in self.numpad_input:
            if event.value == "PRESS":
                if event.type == "NUMPAD_ENTER":
                    self.modifier.steps = self.int_numpad_value
                    self.numpad_value = []
                if event.type == "BACK_SPACE":
                    self.numpad_value.pop()
                else:
                    value = event.unicode
                    self.numpad_value.append(value)

        elif event.type == 'LEFTMOUSE':
            return self.exit_modal(context)

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return self.exit_modal(context, cancelled=True)

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object:
            obj = self.get_active_obj()
            bpy.ops.object.modifier_add(type="SCREW")
            mod = self._get_last_modifier()
            self.initial_mouse = event.mouse_x
            self.mod_name = mod.name
            self.modifier.steps = mod.steps
            self.modifier.screw_offset = 0
            self.modifier.angle = np.radians(360)
            self.modifier.iterations = 1
            self.modifier.axis = "Z"
            self.modifier.use_object_screw_offset = False
            self.modifier.use_normal_calculate = True
            self.modifier.use_normal_flip = False
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}


class CustomLattice(CustomModalOperator, Operator):
    bl_idname = "object.custom_lattice"
    bl_label = "Add Smart Lattice"
    bl_options = {"REGISTER", "UNDO"}
    current_axis = "u"
    axes_dict = dict(zip(list('xyz'), list('uvw')))


    @property
    def current_lattice_axis_val(self):
        return getattr(self.lattice.data, f"points_{self.current_axis}")

    def invoke(self, context, event):
        self.obj = self.get_active_obj()
        bpy.ops.object.add(type="LATTICE")
        self.lattice = self.get_active_obj()
        if not self.obj:
            return {"FINISHED"}
        else:
            context.view_layer.objects.active = self.obj
        bpy.ops.object.modifier_add(type="LATTICE")
        lat_mod = self._get_last_modifier()
        lat_mod.object = self.lattice
        dims = self.obj.dimensions
        ldims = self.lattice.dimensions
        scale_fac = Vector([d / l for l, d in zip(ldims, dims)])
        mx = self.obj.matrix_world
        center = utils.get_bbox_center(self.obj, mx)
        self.lattice.name = f"lattice_{self.obj.name}"
        self.lattice.location = center
        self.lattice.rotation_euler = self.obj.rotation_euler
        self.lattice.scale *= scale_fac
        self.lattice.data.points_u = 3
        self.lattice.data.points_v = 3
        self.lattice.data.points_w = 3
        self.mod = self._get_last_modifier()
        
        context.window_manager.modal_handler_add(self)
        print("ADDED MODAL")
        return {"RUNNING_MODAL"}

        
        
    @property
    def get_info_msg(self):
        lines = [f"CURRENT AXIS: {self.current_axis.upper()}"]
        for ax in list("uvw"):
            letter = ax.upper()
            val = getattr(self.lattice.data, f'points_{ax}')
            lines.append(f"{letter}: {val}")
        
        return ', '.join(lines)


    def modal(self, context, event):
        e = event
        et = e.type
        self.display_modal_info(self.get_info_msg, context)
        if et in list('UVW'):
            self.current_axis = et.lower()
        elif et in list('XYZ'):
            self.current_axis = self.axes_dict[et.lower()]
        elif et in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            curr_val = self.current_lattice_axis_val
            if "DOWN" in et:
                setattr(self.lattice.data, f'points_{self.current_axis}', curr_val - 1)
            else:
                setattr(self.lattice.data, f'points_{self.current_axis}', curr_val + 1)
        elif event.type == "LEFTMOUSE":
            self._clear_info(context)
            return {"FINISHED"}
        elif event.type in {"RIGHTMOUSE", "ESC"}:
            self._clear_info(context)
            bpy.ops.object.modifier_remove(modifier=self.mod.name)
            context.collection.objects.unlink(self.lattice)
            return {"CANCELLED"}

        

        return {'RUNNING_MODAL'}


class AddDisplaceCustom(CustomModalOperator, Operator):
    bl_idname = "object.custom_displace"
    bl_label = "Add Custom Displace"
    bl_options = {"REGISTER", "UNDO"}

    strength: bpy.props.FloatProperty()
    texture = bpy.props.StringProperty()
    size: bpy.props.FloatProperty()
    contrast: bpy.props.FloatProperty()

    textures = ['Clouds', 'Musgrave', 'Voronoi', 'Wood']
    current_texture_index = 0
    transform_axis = "z"
    texture_adjust_channel = None
    inverted = 1
    rotating = False
    scaling = False
    vals_reset = True
    texture_properties = {
        "MUSGRAVE": {
            "basis": "noise_basis",
            "type": "musgrave_type",
            "basis_list": [
                "BLENDER_ORIGINAL",
                "VORONOI_F1",
                "VORONOI_F2_F1",
                "VORONOI_F2",
                "VORONOI_F3",
                "VORONOI_F4",
                "ORIGINAL_PERLIN",
                "VORONOI_CRACKLE",
                "IMPROVED_PERLIN",
                "CELL_NOISE",
            ],
            "type_list": [
                "HETERO_TERRAIN",
                "FBM",
                "HYBRID_MULTIFRACTAL",
                "RIDGED_MULTIFRACTAL",
                "MULTIFRACTAL",
            ],
            "mod_channel": {
                "D": "dimension_max",
                "L": "lacunarity",
                "O": "octaves",
                "I": "noise_intensity",
                "B": "intensity",
                "C": "contrast",
                "S": "noise_scale",
            },
            'default_vals': {},
        },
        "CLOUDS": {
            "basis": "noise_basis",
            "type": "noise_type",
            "basis_list": [
                "BLENDER_ORIGINAL",
                "VORONOI_F1",
                "VORONOI_F2_F1",
                "VORONOI_F2",
                "VORONOI_F3",
                "VORONOI_F4",
                "ORIGINAL_PERLIN",
                "VORONOI_CRACKLE",
                "IMPROVED_PERLIN",
                "CELL_NOISE",
            ],
            "type_list": ["SOFT_NOISE", "HARD_NOISE"],
            "mod_channel": {
                "B": "intensity",
                "C": "contrast",
                "S": "noise_scale",
            },
            'default_vals': {},
        },
        "VORONOI": {
            "basis": "distance_metric",
            "type": "color_mode",
            "basis_list": [
                "DISTANCE",
                "MANHATTAN",
                "CHEBYCHEV",
                "MINKOWSKI",
            ],
            "type_list": [
                'POSITION',
                'POSITION_OUTLINE',
                'POSITION_OUTLINE_INTENSITY',
                'INTENSITY',
            ],
            "mod_channel": {
                "B": "intensity",
                "C": "contrast",
                "S": "noise_scale",
            },
            'default_vals': {},
        },
        "WOOD": {
            "basis": "noise_basis_2",
            "type": "wood_type",
            "basis_list": [
                "SIN",
                "SAW",
                "TRI",
            ],
            "type_list": [
                'RINGNOISE',
                'BANDS',
                'RINGS',
                'BANDNOISE',
            ],
            "mod_channel": {
                "B": "intensity",
                "C": "contrast",
                "S": "noise_scale",
            },
            'default_vals': {},
        },
    }

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH"

    @property
    def last_texture(self):
        return bpy.data.textures[:][-1]

    @property
    def curr_text_props(self):
        type = self.current_texture.type
        return self.texture_properties[type]

    @property
    def all_scene_disp_textures(self):
        d_textures = []
        for t in bpy.data.textures[:]:
            try:
                if t['is_displace']:
                    d_textures.append(t)
            except KeyError:
                continue
        return d_textures

    def _init_textures(self):
        text_attrs = [t for t in self.textures if t]
        for name in text_attrs:
            textype = name.upper()
            bpy.ops.texture.new()
            tex = self.last_texture
            tex.name = f"Displace_{name}"
            tex.type = textype
            tex['is_displace'] = True
            tex = self.last_texture
            props = self.texture_properties[textype]
            for chan in props['mod_channel'].values():
                val = getattr(tex, chan)
                self.texture_properties[textype]['default_vals'][chan] = val
        self.current_texture = bpy.data.textures[self.current_texture_index]
        self.mod.texture = self.current_texture

    def _init_coords_empty(self):
        bpy.ops.object.add(location=self.obj.location)
        self.empty = self.get_last_added_object()
        self.empty.name = "Displace_Coordinates"
        self.empty.empty_display_size = 0.1
        self.empty.empty_display_type = "SPHERE"

    def _init_modifier(self, context):
        context.view_layer.objects.active = self.obj
        bpy.ops.object.modifier_add(type="DISPLACE")
        self.mod = self._get_last_modifier()
        self.mod.texture_coords = "OBJECT"
        self.mod.texture_coords_object = self.empty
        self.mod.strength = 0

    def init_tests(self, context):
        texts = bpy.data.textures[:]
        for t in texts:
            bpy.data.textures.remove(t)
        for mod in self.obj.modifiers[:]:
            if mod.type == "DISPLACE":
                bpy.ops.object.modifier_remove(modifier=mod.name)
        try:
            mt = bpy.data.objects['Displace_Coordinates']
            self.set_active_and_selected(context, mt)
            self.set_active_and_selected(context, self.obj, selected=False)
            bpy.ops.object.delete()
            self.set_active_and_selected(context, self.obj)
        except KeyError:
            pass

    def invoke(self, context, event):
        self.init_x = event.mouse_x
        self.init_y = event.mouse_y
        self.obj = self.get_active_obj()
        ### delete this after testing
        # self.init_tests(context)
        ###
        self.init_loc = self.obj.location
        self.init_rot = 0
        self.init_scale = 0
        self._init_coords_empty()
        self._init_modifier(context)
        self._init_textures()
        context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        # create collection for displace_coord objects
        colls = [coll.name for coll in bpy.data.collections[:]]
        self.active_coll = context.collection
        if "DisplaceCoords" not in colls:
            self.dp_coll = bpy.data.collections.new('DisplaceCoords')
            self.scene_coll = bpy.data.scenes['Scene'].collection
            self.scene_coll.children.link(self.dp_coll)
            self.dp_coll.hide_viewport = True
        else:
            self.dp_coll = bpy.data.collections['DisplaceCoords']
        self.dp_coll.objects.link(self.empty)
        self.active_coll.objects.unlink(self.empty)
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def generate_msg(self):
        def get_float_fmt(items):
            return '\n'.join([f"{amt:.2f}" for amt in items])

        rot_ax = self.transform_axis.upper()
        rot_amt = get_float_fmt(self.empty.rotation_euler)
        scale = get_float_fmt(self.empty.scale)[0]
        c_text = self.current_texture.type
        c_name = self.current_texture.name
        lines = [
            "MOVE: ALT",
            "ROTATE: CTRL",
            "SCALE: MOUSEWHEEL",
            f"ROTATION AXIS: {rot_ax}",
            f"ROTATION: {rot_amt}",
            f"SCALE: {scale}",
            f"TEXTURE_TYPE: {c_text}",
            f"TEXTURE_NAME: {c_name}",
        ]
        mod = self.mod_channel

        if mod is not None:
            chan = mod.upper().replace("_", " ")
            tac_msg = f"ADJUST CHANNEL: {chan}"
            lines.append(tac_msg)
        return ', '.join(lines)

    def get_mouse_val(self, event, multiplier, clamp_range=1):
        location = []
        for axis in list('xy'):
            init_loc = getattr(self, f"init_{axis}")
            mouse_loc = getattr(event, f"mouse_{axis}")
            val = (init_loc - mouse_loc) * multiplier
            loc = utils.clamp(val, -clamp_range, clamp_range)
            location.append(val)
        location.append(0.0)
        return Vector(location)

    def _new_texture_index(self, prev=False):
        if prev:
            addend = -1
        else:
            addend = 1
        return (self.current_texture_index + addend) % len(self.all_scene_disp_textures)

    def _switch_textures(self, prev=False):
        new_index = self._new_texture_index(prev=prev)
        self.current_texture_index = new_index
        self.current_texture = self.all_scene_disp_textures[new_index]
        self.mod.texture = self.current_texture

    def set_adj_chan(self, channel=None):
        if self.texture_adjust_channel is None:
            self.texture_adjust_channel = channel
        elif self.mod_channel is None:
            self.texture_adjust_channel = None
        else:
            self.texture_adjust_channel = channel

    @property
    def mod_channel(self):
        props = self.curr_text_props
        opts = props["mod_channel"]
        channel = self.texture_adjust_channel
        try:
            return opts[channel]
        except KeyError:
            return None

    def adjust_channel(self, val):
        if self.mod_channel is not None:
            new_val = getattr(self.current_texture, self.mod_channel) + (val.x * 0.1)
            setattr(self.current_texture, self.mod_channel, new_val)

    def cleanup_textures(self):
        textures = bpy.data.textures[:]

        for tex in textures:
            if "Displace" in tex.name and tex.users == 0:
                bpy.data.textures.remove(tex)

    def change_texture_attr(self, attr_type="basis", prev=False):
        if prev:
            addend = -1
        else:
            addend = 1
        type = self.current_texture.type
        text = self.texture_properties[type]
        attr = text[attr_type]
        attr_list = self.texture_properties[type][f"{attr_type}_list"]
        current_attr = getattr(self.current_texture, attr)
        curr_index = attr_list.index(current_attr)
        new_index = (curr_index + addend) % len(attr_list)
        new_attr = attr_list[new_index]
        setattr(self.current_texture, attr, new_attr)

    def modal(self, context, event):
        msg = self.generate_msg()
        self.display_modal_info(msg, context)
        if event.shift:
            multiplier = 0.001
        else:
            multiplier = 0.01
        self.mod.strength = self.strength * self.inverted
        if event.type == "MOUSEMOVE":
            val = self.get_mouse_val(event, multiplier)
            self.adjust_channel(val)

            if event.alt:
                self.set_adj_chan()
                self.empty.location = self.init_loc + val
            elif self.rotating:
                self.set_adj_chan()
                setattr(self.empty.rotation_euler, self.transform_axis, self.init_rot + val[0])
            elif self.scaling:
                self.set_adj_chan()
                setattr(self.empty.scale, self.transform_axis, self.init_scale + val[0])
            else:
                val = (self.init_x - event.mouse_x) * multiplier
                self.strength = utils.clamp(val, -3, 3)

        # MOUSEWHEEL ADJUST SCALE
        elif event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            scale_mod = (multiplier * 10) + 1
            if event.type == "WHEELUPMOUSE":
                self.empty.scale *= scale_mod
            else:
                self.empty.scale /= scale_mod
        elif event.value == "PRESS":
            e = event.type
            prev = False
            if event.shift:
                prev = True
            # SWITCH TEXTURE TYPE
            if e == "TAB":
                self._switch_textures(prev=prev)
            elif e == "Q":
                self.change_texture_attr(prev=prev)
            elif e == "W":
                self.change_texture_attr(attr_type="type", prev=prev)
            elif e == "E":
                if not self.vals_reset:
                    props = self.curr_text_props
                    for k, v in props['default_vals'].items():
                        setattr(self.current_texture, k, v)
                    self.set_adj_chan()
                    self.vals_reset = not self.vals_reset
            elif e == "S":
                if not self.scaling:
                    self.rotating = False
                self.scaling = not self.scaling
            elif e == "R":
                if not self.rotating:
                    self.scaling = False
                self.rotating = not self.rotating
            # CHANGE ROTATION AXIS
            elif e in list("XYZ"):
                self.transform_axis = event.unicode.lower()
            # CHANGE TEXTURE ADJUST CHANNEL
            elif e in list("BCDOLIT"):
                self.vals_reset = not self.vals_reset
                if self.texture_adjust_channel == e:
                    self.set_adj_chan()
                else:
                    self.set_adj_chan(e)
            # INVERT STRENGTH
            elif e == "N":
                self.inverted *= -1

        elif event.type == "LEFTMOUSE":
            self.cleanup_textures()
            self._clear_info(context)

            return {"FINISHED"}
        elif event.type in {"RIGHTMOUSE", "ESC"}:
            self._clear_info(context)
            bpy.ops.object.modifier_remove(modifier=self.mod.name)
            self.cleanup_textures()
            self.dp_coll.objects.unlink(self.empty)
            if len(self.dp_coll.objects[:]) == 0:
                self.scene_coll.children.unlink(self.dp_coll)

            return {"CANCELLED"}
        return {"RUNNING_MODAL"}


class ToggleClipping(Operator):
    bl_idname = "object.toggle_mirror_clipping"
    bl_label = "Toggle Clipping"
    bl_description = "Toggles Clipping on Any Mirror Modifiers"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        mods = [mod for mod in obj.modifiers[:] if mod.type == "MIRROR"]
        if mods:
            for mod in mods:
                clip_state = mod.use_clip
                mod.use_clip = not clip_state
        return {"FINISHED"}


class ToggleSubDivVisibility(Operator):
    bl_idname = "object.toggle_subdiv_vis"
    bl_label = "Toggle SubDiv Vis"
    bl_description = "Toggles Subdiv Visibility"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        self.sel_objs = context.selected_objects
        self.show_viewport = self.min_subsurf_visibility

        return self.execute(context)

    @property
    def ss_objs(self):
        objs = []
        for obj in self.sel_objs:
            mods = [mod.type for mod in obj.modifiers[:]]
            if "SUBSURF" in mods:
                objs.append(obj)
        return objs

    def is_visible(self, obj):
        for mod in obj.modifiers[:]:
            if mod.type == "SUBSURF":
                return mod.show_viewport

    @property
    def min_subsurf_visibility(self):
        status = [self.is_visible(obj) for obj in self.ss_objs]
        return min(status)

    def toggle_subsurf(self, obj):
        mods = [mod for mod in obj.modifiers[:] if mod.type == "SUBSURF"]
        if mods:
            for mod in mods:
                visible = mod.show_viewport
                mod.show_viewport = not self.show_viewport

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        for obj in self.ss_objs:
            self.toggle_subsurf(obj)

        return {"FINISHED"}


def menu_func(self, context):
    layout = self.layout
    if context.active_object:
        if len(context.active_object.modifiers):
            col = self.layout.column(align=True)
            row = col.row(align=True)
            row.operator(ToggleClipping.bl_idname, icon='MOD_MIRROR', text="Toggle Clipping")
            row.operator(ToggleSubDivVisibility.bl_idname, icon='MOD_SUBSURF', text="Toggle SubSurf Vis")


classes = {
    CustomAddBevelModifier,
    CustomAddQuickBevSubSurfModifier,
    CustomWeightedNormal,
    CustomSimpleDeform,
    CustomShrinkwrap,
    CustomLattice,
    CustomDecimate,
    CustomRemesh,
    CustomAddMirrorModifier,
    ArrayModalOperator,
    SolidifyModalOperator,
    ScrewModalOperator,
    # AddLatticeCustom,
    AddDisplaceCustom,
    ToggleSubDivVisibility,
    ToggleClipping,
    OBJECT_OT_auto_crease_subdivide,
}


from my_pie_menus import utils


kms = []

addon_keymaps = []


def register():
    utils.register_classes(classes)

    utils.register_keymaps(kms, addon_keymaps)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        utils.unregister_keymaps(kms)
