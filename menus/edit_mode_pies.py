import bpy
from bpy.types import Menu


class MESH_MT_PIE_symmetrize(Menu):
    bl_label = "Select Mode"
    bl_idname = "MESH_MT_PIE_symmetrize"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator_enum("mesh.symmetrize", "direction")


class MESH_MT_edge_menu(Menu):
    # label is displayed at the center of the pie menu.
    bl_idname = "MESH_MT_edge_menu"
    bl_label = "Edge Menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # Left
        col = pie.split().column()
        op = col.operator("mesh.mark_seam", text="Mark Seam")
        op = col.operator("mesh.mark_seam", text="Clear Seam")
        op.clear = True
        col.operator("mesh.boundary_to_seam", text="Boundary to Seam")
        # Right bevel weights
        col = pie.split().column()
        op = col.operator("mesh.toggle_edge_weight", text="Toggle Bevel Weight")
        op.weight_type = "BEVEL"
        op = col.operator("mesh.set_sharp_to_weighted", text="Sharp to Beveled")
        op.weight_type = "BEVEL"
        op = col.operator("mesh.set_boundary_to_weighted", text="Boundary to Beveled")
        op.weight_type = "BEVEL"
        # Bottom - Select Edge loops/rings
        bx = pie.split().box()
        bx.label(text="Select Edges")
        bx.ui_units_y -= 50
        col = bx.column()
        col.operator("mesh.loop_multi_select", text="Edge Rings").ring = True
        col.operator("mesh.loop_multi_select", text="Edge Loops").ring = False
        col.operator("mesh.select_nth")
        # Top select sharp, regions etc.
        bx = pie.split().box()
        bx.label(text="Select")
        col = bx.column()
        col.operator("mesh.edges_select_sharp", text="Sharp Edges")
        col.operator("mesh.loop_to_region", text="Inner Region")
        col.operator("mesh.region_to_loop", text="Boundary Loop")
        # TOP LEFT - set sharps
        col = pie.split().column()
        col.operator("mesh.mark_sharp", text="Mark Sharp")
        op = col.operator("mesh.mark_sharp", text="Clear Sharp")
        op.clear = True
        col.operator("mesh.boundary_to_sharp")
        #
        col = pie.split().column()
        col.operator("mesh.increase_cylinder_res")
        col.operator("mesh.subdivide")
        #
        # Right
        col = pie.split().column()
        op = col.operator("mesh.toggle_edge_weight", text="Toggle Crease")
        op.weight_type = "CREASE"
        op = col.operator("mesh.set_sharp_to_weighted", text="Sharp to Creased")
        op.weight_type = "CREASE"
        op = col.operator("mesh.set_boundary_to_weighted", text="Boundary to Creased")
        op.weight_type = "CREASE"

        # Bottom
        col = pie.split().column()
        col.operator("mesh.edge_rotate", text="Rotate CW").use_ccw = False
        col.operator("mesh.edge_rotate", text="Rotate CCW").use_ccw = True


class MESH_MT_face_menu(Menu):
    # label is displayed at the center of the pie menu.
    bl_idname = "MESH_MT_face_menu"
    bl_label = "Face Pie Menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # Left

        op = pie.operator("mesh.faces_select_linked_flat")
        op = pie.operator("mesh.beautify_fill")
        op = pie.operator("mesh.quads_convert_to_tris")
        box = pie.box()
        box.scale_x *= 0.5
        col = box.column()
        row = col.row()
        spl = row.split()
        spl.operator("mesh.vert_connect_concave")
        spl.operator("mesh.vert_connect_nonplanar")
        row = col.row()
        spl = row.split()
        spl.operator("mesh.fill_holes")
        spl.operator("mesh.face_make_planar")
        row = col.row()
        row.operator("mesh.quick_tris_to_quads")

        col = pie.column()
        op = col.operator("mesh.intersect")
        op = col.operator("mesh.intersect_boolean")
        col = pie.column()
        op = col.operator("mesh.poke")
        op = col.operator("mesh.poke_hole_in_faces")
        pie.operator("mesh.solidify")
        pie.operator("mesh.fill_grid")


class MESH_MT_merge_verts_pie(Menu):
    bl_idname = 'VIEW3D_merge_verts_pie'
    bl_label = "Merge Verts"

    def draw(self, _context):
        layout = self.layout
        pie = layout.menu_pie()

        op = pie.operator('mesh.merge', text="Center")
        op.type = "CENTER"
        op = pie.operator('mesh.merge', text="Collapse")
        op.type = "COLLAPSE"
        pie.operator('mesh.weld_verts_to_active', text="Active")
        op = pie.operator('mesh.remove_doubles', text="Remove Doubles")
        op.use_unselected = True


class MESH_MT_PIE_loop_tools(Menu):
    bl_label = "Loop Tools"
    bl_idname = "MESH_MT_PIE_loop_tools"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        op = pie.operator("mesh.looptools_bridge")
        op = pie.operator("mesh.looptools_circle")
        op = pie.operator("mesh.looptools_curve")
        op = pie.operator("mesh.looptools_flatten")
        op = pie.operator("mesh.looptools_gstretch")
        op = pie.operator("mesh.looptools_loft")
        op = pie.operator("mesh.looptools_relax")
        op = pie.operator("mesh.looptools_space")


classes = (
    MESH_MT_PIE_symmetrize,
    MESH_MT_edge_menu,
    MESH_MT_merge_verts_pie,
    MESH_MT_PIE_loop_tools,
    MESH_MT_face_menu,
)
