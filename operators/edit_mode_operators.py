import bpy
import bmesh
import math
from .custom_operator import CustomOperator, CustomBmeshOperator


class MESH_OT_reduce_cylinder(CustomOperator, bpy.types.Operator):
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


class MESH_OT_reduce_circle_segments(CustomOperator, bpy.types.Operator):
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


class MESH_OT_boundary_to_seam(CustomOperator, bpy.types.Operator):
    bl_idname = "mesh.boundary_to_seam"
    bl_label = "Boundary to Seam"

    def execute(self, context):
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.mark_seam()
        return {"FINISHED"}


class MESH_OT_boundary_to_sharp(CustomOperator, bpy.types.Operator):
    bl_idname = "mesh.boundary_to_sharp"
    bl_label = "Boundary to Sharp"

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.mark_sharp()
        return {"FINISHED"}


class MESH_OT_increase_cylinder_res(CustomOperator, bpy.types.Operator):
    """Double Cylinder Resolution"""

    bl_idname = "mesh.increase_cylinder_res"
    bl_label = "Increase Cylinder Res"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    @staticmethod
    def subdivide():
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.modifier_add(type="SUBSURF")
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.mode_set(mode="EDIT")

    @staticmethod
    def simplify_mesh():
        deg = math.radians(5)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.dissolve_limited(angle_limit=deg)
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.mesh.tris_convert_to_quads()

    def get_bm(self, obj):
        return bmesh.from_edit_mesh(obj.data)

    def edit_crease(self, obj, degrees=50, set=True):
        bm = self.get_bm(obj)
        edges = bm.edges[:]
        deg = math.radians(degrees)
        crease_layer = bm.edges.layers.crease.verify()
        for edge in edges:
            if set:
                try:
                    sharpness = edge.calc_face_angle()
                except ValueError:
                    sharpness = 0
                if sharpness > deg:
                    edge[crease_layer] = 1
            else:
                edge[crease_layer] = 0
        bmesh.update_edit_mesh(obj.data)

    def execute(self, context):
        obj = context.active_object
        self.edit_crease(obj)
        self.subdivide()
        obj = context.active_object
        self.edit_crease(obj, set=False)
        obj = context.active_object
        self.simplify_mesh()
        return {'FINISHED'}


class MESH_OT_quick_tris_to_quads(CustomOperator, bpy.types.Operator):
    bl_idname = "mesh.quick_tris_to_quads"
    bl_label = "Quick Tris to Quads"

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.mesh.tris_convert_to_quads()
        return {"FINISHED"}


class MESH_OT_toggle_edge_weight(CustomBmeshOperator, bpy.types.Operator):

    bl_idname = "mesh.toggle_edge_weight"
    bl_label = "Set Edge Weight"
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

    def verify_weight_layer(self, bm):
        if self.weight_type == "BEVEL":
            self.weight_layer = bm.edges.layers.bevel_weight.verify()
        elif self.weight_type == "CREASE":
            self.weight_layer = bm.edges.layers.crease.verify()

    def execute(self, context):
        self.verify_weight_layer(self.bm)
        self.set_edges_weight()
        bmesh.update_edit_mesh(context.edit_object.data)
        return {"FINISHED"}


class MESH_OT_set_sharp_to_weighted(MESH_OT_toggle_edge_weight, CustomBmeshOperator, bpy.types.Operator):
    bl_idname = "mesh.set_sharp_to_weighted"
    bl_label = "Sharp To Weighted"
    bl_options = {'REGISTER', 'UNDO'}

    weight_type: bpy.props.StringProperty(name="Weight Type", default="BEVEL")
    sharpness: bpy.props.IntProperty(name="Sharpness", default=30)

    @property
    def sharp_angle(self):
        return math.radians(self.sharpness)

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
        self.select_sharp_edges(self.bm, threshold=self.sharp_angle)
        self.verify_weight_layer(self.bm)
        self.set_edges_weight()
        if stored_edges:
            self.select_edges(context, self.bm.edges[:], select=False)
            self.select_edges(context, stored_edges, select=True)
        bmesh.update_edit_mesh(context.edit_object.data)
        return {"FINISHED"}


""  # class MESH_OT_set_sharp_to_weighted(CustomBmeshOperator, bpy.types.Operator):
#     bl_idname = "mesh.set_sharp_to_weighted"
#     bl_label = "Sharp to Beveled"
#     bl_options = {"REGISTER", "UNDO"}
#
#     sharpness: bpy.props.IntProperty(name="Sharpness", default="30")
#     weight_type: bpy.props.StringProperty(name='Weight Type', default="BEVEL")
#
#     @classmethod
#     def poll(cls, context):
#         return cls.edit_obj_poll(context)
#
#     def invoke(self, context, event):
#         self.bmesh(context)
#         return self.execute(context)
#
#     def execute(self, context):
#         obj = self.get_active_obj()
#         edges = self.sel_edges
#         bpy.ops.mesh.select_all(action="DESELECT")
#         bpy.ops.mesh.edges_select_sharp(sharpness=self.sharpness)
#         bpy.ops.mesh.toggle_edge_weight(weight_type=self.weight_type)
#         for edge in edges:
#             edge.select = True
#         self.bm.update_edit_mesh(obj.data)
#         return {"FINISHED"}


classes = (
    MESH_OT_reduce_cylinder,
    MESH_OT_reduce_circle_segments,
    MESH_OT_increase_cylinder_res,
    MESH_OT_boundary_to_sharp,
    MESH_OT_boundary_to_seam,
    MESH_OT_quick_tris_to_quads,
    MESH_OT_toggle_edge_weight,
    MESH_OT_set_sharp_to_weighted,
)
