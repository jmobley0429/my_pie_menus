import bpy
import bmesh
from .custom_operator import CustomOperator


class MESH_OT_reduce_cylinder(bpy.types.Operator):
    """Cut cylinder edges in half, select one edge ring and then execute."""

    bl_idname = "mesh.reduce_cylinder"
    bl_label = "Reduce Cylinder Edges"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == "EDIT_MESH"

    def execute(self, context):
        bpy.ops.mesh.edgering_select("INVOKE_DEFAULT")
        bpy.ops.mesh.select_nth()
        bpy.ops.mesh.loop_multi_select(ring=False)
        bpy.ops.mesh.dissolve_mode(use_verts=True)
        return {'FINISHED'}


class MESH_OT_reduce_circle_segments(bpy.types.Operator):
    """Cut cylinder edges in half, select one edge ring and then execute."""

    bl_idname = "mesh.reduce_circle_segments"
    bl_label = "Reduce Circle Segments"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == "EDIT_MESH"

    def execute(self, context):
        bpy.ops.mesh.loop_multi_select(ring=False)
        bpy.ops.mesh.select_nth()
        bpy.ops.mesh.merge(type='COLLAPSE')
        return {'FINISHED'}


class MESH_OT_boundary_to_seam(bpy.types.Operator):
    bl_idname = "mesh.boundary_to_seam"
    bl_label = "Boundary to Seam"

    def execute(self, context):
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.mark_seam()
        return {"FINISHED"}


class MESH_OT_boundary_to_sharp(bpy.types.Operator):
    bl_idname = "mesh.boundary_to_sharp"
    bl_label = "Boundary to Sharp"

    def execute(self, context):
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.mark_sharp()
        return {"FINISHED"}


class MESH_OT_increase_cylinder_res(bpy.types.Operator):
    """Double Cylinder Resolution"""

    bl_idname = "mesh.increase_cylinder_res"
    bl_label = "Increase Cylinder Res"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == "EDIT_MESH"

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


class MESH_OT_quick_tris_to_quads(bpy.types.Operator):
    bl_idname = "mesh.quick_tris_to_quads"
    bl_label = "Quick Tris to Quads"

    def execute(self, context):
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.mesh.tris_convert_to_quads()
        return {"FINISHED"}


class MESH_OT_toggle_edge_weight(CustomOperator, bpy.types.Operator):

    bl_idname = "mesh.toggle_edge_weight"
    bl_label = "Set Edge Weight"
    bl_options = {'REGISTER', 'UNDO'}

    weight_type: bpy.props.StringProperty(name='weight_type', description='Set weight type', default="BEVEL")

    bm = None

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == "EDIT_MESH"

    @classmethod
    def bmesh(cls, context):
        cls.me = context.edit_object.data
        bm = bmesh.from_edit_mesh(cls.me)
        cls.bm = bm

    def invoke(self, context, event):

        return self.execute(context)

    def execute(self, context):
        self.bmesh(context)
        sel_edges = [e for e in self.bm.edges[:] if e.select]
        if self.weight_type == "BEVEL":
            weight_layer = self.bm.edges.layers.bevel_weight.verify()
        elif self.weight_type == "CREASE":
            weight_layer = self.bm.edges.layers.crease.verify()
        for edge in sel_edges:
            if self.weight_type == "SEAM":
                edge.seam = not edge.seam
            else:
                val = not edge[weight_layer]
                edge[weight_layer] = float(val)

        bmesh.update_edit_mesh(context.edit_object.data)
        self.bm.free()
        return {"FINISHED"}


classes = (
    MESH_OT_reduce_cylinder,
    MESH_OT_reduce_circle_segments,
    MESH_OT_increase_cylinder_res,
    MESH_OT_boundary_to_sharp,
    MESH_OT_boundary_to_seam,
    MESH_OT_quick_tris_to_quads,
    MESH_OT_toggle_edge_weight,
)
