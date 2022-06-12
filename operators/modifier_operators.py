from collections import deque

import bpy
import bmesh
import math
from math import pi
from my_pie_menus.resources import utils
from mathutils import Vector
from .custom_operator import CustomOperator, CustomModalOperator


class CustomAddMirrorModifier(CustomOperator, bpy.types.Operator):
    """Add Mirror Custom Modifier"""

    bl_idname = "object.custom_mirror_modifier"
    bl_label = "Add Custom Mirror"
    bl_parent_id = "CustomOperator"

    mirror_type: bpy.props.StringProperty(
        default="",
    )

    def execute(self, context):
        in_edit_mode = bool(bpy.context.object.mode == "EDIT")
        if in_edit_mode:
            bpy.ops.object.mode_set(mode="OBJECT")

        obj = self.get_active_obj()
        self._bisect_mesh()
        bpy.ops.object.modifier_add(type='MIRROR')
        axis_index = self.mirror_axis
        mirror_mod = obj.modifiers[:][-1]
        for i in range(3):
            mirror_mod.use_axis[i] = False
            mirror_mod.use_bisect_axis[i] = False
        mirror_mod.use_axis[axis_index] = True
        mirror_mod.use_bisect_axis[axis_index] = True
        mirror_mod.use_clip = True
        if self.mirror_type != "Z":
            mirror_mod.use_bisect_flip_axis[axis_index] = True
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

        args = self.bisect_args

        ret = bmesh.ops.bisect_plane(
            bm,
            geom=get_geom(bm),
            dist=0.0001,
            plane_co=(0, 0, 0),
            plane_no=args['plane_no'],
            clear_outer=args['clear_outer'],
            clear_inner=args['clear_inner'],
        )

        bm.to_mesh(me)
        me.update()

    @property
    def mirror_axis(self):
        if self.mirror_type:
            axes = {
                'X': 0,
                'Y': 1,
                'Z': 2,
            }
            return axes[self.mirror_type]

    @property
    def bisect_args(self):
        if self.mirror_type:
            vals = {
                'X': {
                    'plane_no': (1, 0, 0),
                    'clear_inner': False,
                    'clear_outer': True,
                },
                'Y': {
                    'plane_no': (0, 1, 0),
                    'clear_inner': False,
                    'clear_outer': True,
                },
                'Z': {
                    'plane_no': (0, 0, 1),
                    'clear_inner': True,
                    'clear_outer': False,
                },
            }

            return vals[self.mirror_type]


class BevelModifier(CustomOperator):
    def _add_bevel_modifier(self, harden_normals=True):
        obj = self.get_active_obj()
        bpy.ops.object.shade_smooth()
        obj.data.use_auto_smooth = True
        bpy.ops.object.modifier_add(type='BEVEL')
        bevel_mod = obj.modifiers[:][-1]
        bevel_mod.segments = 2
        bevel_mod.width = 0.025
        bevel_mod.harden_normals = harden_normals
        bevel_mod.miter_outer = "MITER_ARC"
        bevel_mod.use_clamp_overlap = False


class CustomAddBevelModifier(BevelModifier, bpy.types.Operator):
    """Add Custom Bevel Modifier"""

    bl_idname = "object.custom_bevel_modifier"
    bl_label = "Add Custom Bevel"
    bl_parent_id = "CustomOperator"

    def execute(self, context):
        self._add_bevel_modifier()
        self.close_modifiers()
        return {"FINISHED"}


class CustomAddQuickBevSubSurfModifier(BevelModifier, bpy.types.Operator):
    """Add Custom Bevel Modifier with Subsurf"""

    bl_idname = "object.custom_bevel_subsurf_modifier"
    bl_label = "Add Custom Bevel Subsurf"
    bl_parent_id = "CustomAddBevelModifier"

    def execute(self, context):
        obj = self.get_active_obj()
        self._add_bevel_modifier(harden_normals=False)
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.ops.object.modifier_add(type='WEIGHTED_NORMAL')
        bpy.ops.object.shade_smooth()
        obj.data.use_auto_smooth = True
        self.close_modifiers()

        return {"FINISHED"}


class CustomWeightedNormal(CustomOperator, bpy.types.Operator):
    """Add Custom Weighted Normal Modifier"""

    bl_idname = "object.custom_weighted_normal"
    bl_label = "Add Custom Weighted Normal"

    def execute(self, context):
        obj = self.get_active_obj()
        obj.data.use_auto_smooth = True
        bpy.ops.object.modifier_add(type="WEIGHTED_NORMAL")
        self.close_modifiers()

        return {"FINISHED"}


class CustomSimpleDeform(CustomModalOperator, bpy.types.Operator):
    """Add Custom Simple Deform Modifier"""

    bl_idname = "object.custom_simple_deform"
    bl_label = "Add Custom Simple Deform"

    angle: bpy.props.FloatProperty(name='angle', description='Deform Angle', default=45.0)
    axis: bpy.props.StringProperty(name='axis', description='Deform Axis', default="Z")
    x: bpy.props.IntProperty(min=0, max=360)
    mod = None

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

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
            self.mod.angle = math.radians(self.angle)
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


class CustomShrinkwrap(CustomOperator, bpy.types.Operator):
    """Add Custom Shrinkwrap Modifier"""

    bl_idname = "object.custom_shrinkwrap"
    bl_label = "Add Custom Shrinkwrap"

    def execute(self, context):
        num_objs = len(bpy.context.selected_objects)
        if num_objs < 2:
            self.report({'INFO'}, 'Select a modified and target object!')
            return {'CANCELLED'}
        mod, target = self.get_mod_and_target_objects()
        bpy.context.view_layer.objects.active = mod
        bpy.ops.object.modifier_add(type="SHRINKWRAP")
        sw = self._get_last_modifier()
        sw.target = target
        sw.offset = 0.01

        return {"FINISHED"}


class CustomLattice(CustomOperator, bpy.types.Operator):
    """Add Custom Lattice Modifier"""

    bl_idname = "object.custom_lattice"
    bl_label = "Add Custom Lattice"

    def execute(self, context):
        bpy.ops.object.modifier_add(type="LATTICE")
        lat = self._get_last_modifier()
        bpy.ops.object.smart_add_lattice()
        obj = self.get_active_obj()
        lat.object = obj
        return {"FINISHED"}


class CustomRemesh(CustomOperator, bpy.types.Operator):
    """Add Custom Remesh Modifier"""

    bl_idname = "object.custom_remesh"
    bl_label = "Add Custom Remesh"

    def execute(self, context):
        bpy.ops.object.modifier_add(type="REMESH")
        mod = self._get_last_modifier()
        mod.voxel_size = 0.025
        mod.use_smooth_shade = True
        return {"FINISHED"}


class CustomDecimate(CustomOperator, bpy.types.Operator):
    """Add Custom Decimate Modifier"""

    bl_idname = "object.custom_decimate"
    bl_label = "Add Custom Decimate"

    def execute(self, context):
        bpy.ops.object.modifier_add(type="DECIMATE")
        mod = self._get_last_modifier()
        mod.ratio = 0.1
        return {"FINISHED"}


class ArrayModalOperator(CustomModalOperator, bpy.types.Operator):
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
                snap_val = math.floor(delta * (-multiplier)) + 1
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
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        print('Starting Modal')
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


class SolidifyModalOperator(CustomModalOperator, bpy.types.Operator):
    bl_idname = "object.solidify_modal"
    bl_label = "Solidify Modal"

    thickness: bpy.props.FloatProperty()

    def modal(self, context, event):
        print(event.type)
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


class ScrewModalOperator(CustomModalOperator, bpy.types.Operator):
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

    def set_screw_angle(self, delta, multiplier):
        angle = delta * multiplier
        new_angle = self.modifier.angle - math.radians(angle)
        self.modifier.angle = utils.clamp(new_angle, 0, 2 * pi)

    def set_screw_count(self, event_type):
        if event_type == "WHEELUPMOUSE":
            self.modifier.steps += 1
        else:
            self.modifier.steps -= 1

    def _log_info_msg(self):
        mod = self.modifier
        msg = [
            f"Degrees: {math.degrees(mod.angle)}",
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
            self.modifier.angle = math.radians(360)
            self.modifier.iterations = 1
            self.modifier.axis = "Z"
            self.modifier.use_object_screw_offset = False
            self.modifier.use_normal_calculate = True
            self.modifier.use_normal_flip = False
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}


class AddLatticeCustom(CustomOperator, bpy.types.Operator):
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
        obj = self.get_active_obj()

        if obj:
            size = obj.dimensions
            loc = obj.matrix_world.translation

            bpy.ops.object.add(type="LATTICE", location=loc)
            lattice = self.get_active_obj()
            lattice.dimensions = size
            lattice.data.points_u = self._get_uvw_res(size.x)
            lattice.data.points_v = self._get_uvw_res(size.y)
            lattice.data.points_w = self._get_uvw_res(size.z)

        else:
            bpy.ops.object.add(type="LATTICE")

        return {'FINISHED'}


class AddDisplaceCustom(CustomModalOperator, bpy.types.Operator):
    bl_idname = "object.custom_displace"
    bl_label = "Add Custom Displace"
    bl_options = {"REGISTER", "UNDO"}

    strength: bpy.props.FloatProperty()
    texture = bpy.props.StringProperty()
    size: bpy.props.FloatProperty()
    contrast: bpy.props.FloatProperty()

    textures = ['Clouds', 'Musgrave', 'Voronoi', 'Wood']
    current_texture_index = 0
    rot_axis = "x"
    texture_adjust_channel = None
    texture_adjust_options = {
        "D": "dimension_max",
        "L": "lacunarity",
        "O": "octaves",
        "I": "noise_intensity",
        "B": "intensity",
        "C": "contrast",
    }

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH"

    @property
    def last_texture(self):
        return bpy.data.textures[:][-1]

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
        ### delete this after testing
        texts = bpy.data.textures[:]
        for t in texts:
            bpy.data.textures.remove(t)
        ###
        text_attrs = [t for t in self.textures if t]
        for name in text_attrs:
            bpy.ops.texture.new()
            tex = self.last_texture
            tex.name = f"Displace_{name}"
            tex.type = name.upper()
            tex['is_displace'] = True
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
        self.init_tests(context)
        ###

        self.init_loc = self.obj.location
        self.init_rot = 0
        self._init_coords_empty()
        self._init_modifier(context)
        self._init_textures()
        context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def generate_msg(self):
        lines = [f"ROTATION AXIS: {self.rot_axis.upper()}", "SCALE: {self.empty.scale.xyz}, {tac_msg}"]
        if self.texture_adjust_channel is not None:
            chan = self.texture_adjust_options[self.texture_adjust_channel].upper().replace("_", " ")
            tac_msg = f"ADJUST CHANNEL: {chan}"
            lines.append(tac_msg)
        return ', '.join(lines)

    def get_mouse_val(self, event, multiplier, clamp_range=1):
        location = []
        for axis in list('xy'):
            init_loc = getattr(self, f"init_{axis}")
            mouse_loc = getattr(event, f"mouse_{axis}")
            val = (init_loc - mouse_loc) * multiplier
            loc = utils.clamp(val, -clamp_range, clamp_range) * -1
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

    def modal(self, context, event):
        msg = self.generate_msg()
        self.display_modal_info(msg, context)

        if event.shift:
            multiplier = 0.001
        else:
            multiplier = 0.01

        if event.type == "MOUSEMOVE":

            val = self.get_mouse_val(event, multiplier)
            if self.texture_adjust_channel is not None:
                mod_channel = self.texture_adjust_options[self.texture_adjust_channel]
                if self.texture_adjust_channel in list('DOIL'):
                    if self.current_texture.type != "MUSGRAVE":
                        return {"RUNNING_MODAL"}
                new_val = getattr(self.current_texture, mod_channel) + val.x
                setattr(self.current_texture, mod_channel, new_val)

            if event.alt:
                self.empty.location = self.init_loc + val
            elif event.ctrl:
                setattr(self.empty.rotation_euler, self.rot_axis, self.init_rot + val[0])
            else:
                val = (self.init_x - event.mouse_x) * multiplier
                self.strength = utils.clamp(val, -3, 3)
                self.mod.strength = self.strength
        elif event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            scale_mod = (multiplier * 10) + 1
            if event.type == "WHEELUPMOUSE":
                self.empty.scale *= scale_mod
            else:
                self.empty.scale /= scale_mod
        elif event.value == "PRESS":
            if event.type == "TAB":
                if event.shift:
                    self._switch_textures(prev=True)
                else:
                    self._switch_textures()
            elif event.type in list("XYZ"):
                self.rot_axis = event.unicode.lower()
            elif event.type in list("BCDOLI"):
                if self.texture_adjust_channel == event.type:
                    self.texture_adjust_channel = None
                else:
                    self.texture_adjust_channel = event.type

        elif event.type == "LEFTMOUSE":
            self._clear_info()
            return {"FINISHED"}
        elif event.type in {"RIGHTMOUSE", "ESC"}:
            self._clear_info()
            bpy.ops.object.modifier_remove(modifier=self.mod.name)
            self.obj.select_set(False)
            self.empty.select_set(True)
            bpy.ops.object.delete()

            return {"CANCELLED"}
        return {"RUNNING_MODAL"}


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
    AddLatticeCustom,
    AddDisplaceCustom,
}
