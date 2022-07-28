import bpy
from bpy.types import Operator
import bmesh
import numpy as np
from .custom_operator import (
    CustomOperator,
    CustomModalOperator,
    CustomBmeshOperator,
)


class MESH_OT_reduce_cylinder(CustomOperator, Operator):
    """Cut cylinder edges in half, select one edge ring and then execute."""

    bl_idname = "mesh.reduce_cylinder"
    bl_label = "Reduce Cylinder Edges"

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        bpy.ops.mesh.edgering_select("INVOKE_DEFAULT")
        bpy.ops.mesh.select_nth()
        bpy.ops.mesh.loop_multi_select(ring=False)
        bpy.ops.mesh.dissolve_mode(use_verts=True)
        return {'FINISHED'}


class MESH_OT_reduce_circle_segments(CustomOperator, Operator):
    """Cut cylinder edges in half, select one edge ring and then execute."""

    bl_idname = "mesh.reduce_circle_segments"
    bl_label = "Reduce Circle Segments"

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        bpy.ops.mesh.loop_multi_select(ring=False)
        bpy.ops.mesh.select_nth()
        bpy.ops.mesh.merge(type='COLLAPSE')
        return {'FINISHED'}


class MESH_OT_boundary_to_seam(CustomOperator, Operator):
    bl_idname = "mesh.boundary_to_seam"
    bl_label = "Boundary to Seam"

    def execute(self, context):
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.mark_seam()
        return {"FINISHED"}


class MESH_OT_boundary_to_sharp(CustomOperator, Operator):
    bl_idname = "mesh.boundary_to_sharp"
    bl_label = "Boundary to Sharp"

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.mark_sharp()
        return {"FINISHED"}


class MESH_OT_increase_cylinder_res(CustomOperator, Operator):
    """Double Cylinder Resolution"""

    bl_idname = "mesh.increase_cylinder_res"
    bl_label = "Increase Cylinder Res"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bpy.ops.mesh.loop_multi_select(ring=True)
        bpy.ops.mesh.loop_multi_select(ring=False)
        sel_edges = [e for e in bm.edges[:] if e.select]
        bmesh.ops.subdivide_edges(bm, edges=sel_edges, cuts=1)
        bmesh.update_edit_mesh(me)
        bpy.ops.mesh.looptools_circle()
        return {'FINISHED'}


class MESH_OT_quick_tris_to_quads(CustomOperator, Operator):
    bl_idname = "mesh.quick_tris_to_quads"
    bl_label = "Quick Tris to Quads"

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.mesh.tris_convert_to_quads()
        return {"FINISHED"}


class MESH_OT_toggle_edge_weight(CustomBmeshOperator, Operator):

    bl_idname = "mesh.toggle_edge_weight"
    bl_label = "Set Edge Weight"
    desc_vals = [
        "Set edge weight on selected edges. Default toggle all selected edges to opposite value.",
        "CTRL - Clear all edges.",
        "ALT - Set all edges weight to 1",
    ]
    bl_description = '\n'.join(desc_vals)
    bl_options = {'REGISTER', 'UNDO'}

    weight_type: bpy.props.StringProperty(name='Weight Type')
    clear = None

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def invoke(self, context, event):
        if event.alt:
            self.clear = True
        elif event.ctrl:
            self.clear = False
        self.bmesh(context)
        return self.execute(context)

    def set_edge_weight(self, edge):
        if self.clear is not None:
            val = self.clear
        else:
            val = not edge[self.weight_layer]
        edge[self.weight_layer] = float(val)

    def set_edges_weight(self):
        for edge in self.sel_edges:
            try:
                self.set_edge_weight(edge)
            except ReferenceError:
                self.bmesh(context)
                self.set_edges_weight()

    def verify_weight_layer(self):
        if self.weight_type == "BEVEL":
            self.weight_layer = self.bm.edges.layers.bevel_weight.verify()
        elif self.weight_type == "CREASE":
            self.weight_layer = self.bm.edges.layers.crease.verify()

    def execute(self, context):
        self.verify_weight_layer()
        self.set_edges_weight()
        bmesh.update_edit_mesh(context.edit_object.data)
        return {"FINISHED"}


class MESH_OT_set_sharp_to_weighted(MESH_OT_toggle_edge_weight, CustomBmeshOperator, Operator):
    bl_idname = "mesh.set_sharp_to_weighted"
    bl_label = "Sharp To Weighted"
    bl_options = {'REGISTER', 'UNDO'}

    weight_type: bpy.props.StringProperty(name="Weight Type", default="BEVEL")
    sharpness: bpy.props.IntProperty(name="Sharpness", default=30)

    @property
    def sharp_angle(self):
        return np.radians(self.sharpness)

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def invoke(self, context, event):
        self.bmesh(context)
        return self.execute(context)

    def execute(self, context):
        obj = self.get_active_obj()
        stored_edges = [e for e in self.sel_edges]
        self.select_edges(context, self.bm.edges[:], select=False)
        self.select_sharp_edges(threshold=self.sharp_angle)
        self.verify_weight_layer()
        self.set_edges_weight()
        if stored_edges:
            self.select_edges(context, self.bm.edges[:], select=False)
            self.select_edges(context, stored_edges, select=True)
        bmesh.update_edit_mesh(context.edit_object.data)
        return {"FINISHED"}


class MESH_OT_set_boundary_to_weighted(MESH_OT_toggle_edge_weight, CustomBmeshOperator, Operator):
    bl_idname = "mesh.set_boundary_to_weighted"
    bl_label = "Boundary To Weighted"
    bl_options = {'REGISTER', 'UNDO'}

    weight_type: bpy.props.StringProperty(name="Weight Type", default="BEVEL")

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def invoke(self, context, event):
        self.bmesh(context)
        return self.execute(context)

    def execute(self, context):
        obj = self.get_active_obj()
        stored_edges = [e for e in self.sel_edges]
        self.select_edges(context, self.bm.edges[:], select=False, skip_callback_func=self.is_boundary_edge)
        self.verify_weight_layer()
        self.set_edges_weight()
        self.bmesh(context)
        if stored_edges:
            self.select_edges(context, self.bm.edges[:], select=False)
            self.select_edges(context, stored_edges, select=True)
        bmesh.update_edit_mesh(context.edit_object.data)
        return {"FINISHED"}


class MESH_OT_weld_verts_to_active(Operator):

    '''Weld all selected verts to active vertex.'''

    bl_idname = "mesh.weld_verts_to_active"
    bl_label = "Weld to Active"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH" and "EDIT" in context.mode

    def get_bmesh(self, context):
        self.obj = context.edit_object
        self.mesh = self.obj.data
        self.bm = bmesh.from_edit_mesh(self.mesh)

    def execute(self, context):
        try:
            bpy.ops.view3d.snap_selected_to_active()
            bpy.ops.mesh.remove_doubles(use_unselected=True)
        except RuntimeError:
            bpy.ops.mesh.merge(type="CENTER")
        return {"FINISHED"}


class VIEW3D_OT_toggle_annotate(Operator):
    bl_idname = "view3d.toggle_annotate"
    bl_label = "Toggle Annotate"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        tools = context.workspace.tools
        mode = context.mode
        curr_tool = tools.from_space_view3d_mode(mode, create=False).idname
        if curr_tool != "builtin.annotate":
            bpy.ops.wm.tool_set_by_id(name="builtin.annotate")
        else:
            bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
        return {"FINISHED"}


class MESH_OT_poke_hole_in_faces(CustomBmeshOperator, CustomModalOperator, Operator):
    bl_idname = "mesh.poke_hole_in_faces"
    bl_label = "Poke Hole in Face"
    bl_options = {'REGISTER', 'UNDO'}

    offset_multiplier: bpy.props.FloatProperty(name="Offset Multiplier", default=0.2)
    bridge = False

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def poke_hole(self):
        ret = bmesh.ops.poke(self.bm, faces=self.sel_faces)
        center = ret['verts'][:]
        self.select_elem_in_list(self.bm.verts[:], center)
        del ret
        for face in self.bm.faces[:]:
            face.select_set(False)
        self.bm.select_flush_mode()
        ret = bmesh.ops.bevel(self.bm, geom=center, offset=self.offset_amt, segments=2)
        verts = ret['verts']
        faces = ret['faces']
        del ret
        bmesh.ops.delete(self.bm, geom=faces, context="FACES")
        self.select_elem_in_list(self.bm.verts[:], verts)
        bmesh.update_edit_mesh(self.mesh)
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.looptools_circle()

    def invoke(self, context, event):
        self.bmesh(context)
        self.sel_faces = [f for f in self.bm.faces[:] if f.select]
        self.offset_amt = np.mean([f.calc_area() for f in self.sel_faces]) * self.offset_multiplier
        # self.init_mouse_x = event.mouse_x
        if event.alt:
            self.bridge = True
        return self.execute(context)

    def execute(self, context):
        self.poke_hole()
        if self.bridge:
            bpy.ops.mesh.bridge_edge_loops()
        return {"FINISHED"}


classes = (
    MESH_OT_reduce_cylinder,
    MESH_OT_reduce_circle_segments,
    MESH_OT_increase_cylinder_res,
    MESH_OT_boundary_to_sharp,
    MESH_OT_boundary_to_seam,
    MESH_OT_quick_tris_to_quads,
    MESH_OT_toggle_edge_weight,
    MESH_OT_set_sharp_to_weighted,
    MESH_OT_set_boundary_to_weighted,
    MESH_OT_weld_verts_to_active,
    VIEW3D_OT_toggle_annotate,
    MESH_OT_poke_hole_in_faces,
)
