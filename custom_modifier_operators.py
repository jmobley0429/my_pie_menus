import bpy
import bmesh
from .custom_operator import CustomOperator


class CustomAddMirrorModifier(CustomOperator, bpy.types.Operator):
    """Add Mirror Custom Modifier"""

    bl_idname = "object.custom_mirror_modifier"
    bl_label = "Add Custom Mirror"
    bl_parent_id = "CustomOperator"

    mirror_type: bpy.props.StringProperty(
        default="",
    )

    def execute(self, context):
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
        bevel_mod.width = 0.05
        bevel_mod.harden_normals = harden_normals
        bevel_mod.miter_outer = "MITER_ARC"


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


class CustomSimpleDeform(CustomOperator, bpy.types.Operator):
    """Add Custom Weighted Normal Modifier"""

    bl_idname = "object.custom_simple_deform"
    bl_label = "Add Custom Simple Deform"

    def execute(self, context):
        obj = self.get_active_obj()
        loc = obj.location
        bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
        mod = self._get_last_modifier()
        mod.deform_method = 'BEND'
        mod.deform_axis = 'Z'
        bpy.ops.object.add(type="EMPTY")
        empty = self.get_last_added_object()
        empty.name = "Simple_Deform_Pivot"
        mod.origin = empty
        self.close_modifiers()

        return {"FINISHED"}


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
