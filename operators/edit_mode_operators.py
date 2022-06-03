import bpy


class MESH_OT_reduce_cylinder(bpy.types.Operator):
    """Cut cylinder edges in half, select one edge ring and then execute."""

    bl_idname = "mesh.reduce_cylinder"
    bl_label = "Reduce Cylinder Edges"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.ops.mesh.edgering_select("INVOKE_DEFAULT")
        bpy.ops.mesh.select_nth()
        bpy.ops.mesh.loop_multi_select(ring=False)
        bpy.ops.mesh.dissolve_mode(use_verts=True)
        return {'FINISHED'}


class MESH_OT_boundary_to_seam(bpy.types.Operator):
    bl_idname = "mesh.boundary_to_seam"
    bl_label = "Boundary to Seam"

    def execute(self, context):
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.mark_seam()
        return {"FINISHED"}


class MESH_OT_increase_cylinder_res(bpy.types.Operator):
    """Double Cylinder Resolution"""

    bl_idname = "mesh.increase_cylinder_res"
    bl_label = "Increase Cylinder Res"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

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


classes = (
    MESH_OT_reduce_cylinder,
    MESH_OT_increase_cylinder_res,
    MESH_OT_boundary_to_seam,
)
