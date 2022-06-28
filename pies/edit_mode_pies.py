import bpy
from bpy.types import Menu


class MESH_MT_PIE_symmetrize(Menu):
    bl_label = "Select Mode"
    bl_idname = "MESH_MT_PIE_symmetrize"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator_enum("mesh.symmetrize", "direction")


class PIE_MT_edge_menu(Menu):
    # label is displayed at the center of the pie menu.
    bl_idname = "PIE_MT_edge_menu"
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
        # Right
        col = pie.split().column()
        op = col.operator("mesh.toggle_edge_weight", text="Toggle Bevel Weight")
        op.weight_type = "BEVEL"
        # Bottom

        bx = pie.split().box()
        bx.label(text="Select Edges")
        bx.ui_units_y -= 50
        col = bx.column()
        col.operator("mesh.loop_multi_select", text="Edge Rings").ring = True
        col.operator("mesh.loop_multi_select", text="Edge Loops").ring = False
        col.operator("mesh.select_nth")
        # Top
        bx = pie.split().box()
        bx.label(text="Select")
        col = bx.column()
        col.operator("mesh.edges_select_sharp", text="Sharp Edges")
        col.operator("mesh.loop_to_region", text="Inner Region")
        col.operator("mesh.region_to_loop", text="Boundary Loop")
        #
        col = pie.split().column()
        col.operator("mesh.mark_sharp", text="Mark Sharp")
        op = col.operator("mesh.mark_sharp", text="Clear Sharp")
        op.clear = True
        col.operator("mesh.boundary_to_sharp")
        #
        col = pie.split().column()
        col.operator("mesh.bridge_edge_loops")
        col.operator("mesh.subdivide")
        #
        # Right
        col = pie.split().column()
        op = col.operator("mesh.toggle_edge_weight", text="Toggle Crease")
        op.weight_type = "CREASE"

        # Bottom
        col = pie.split().column()
        col.operator("mesh.edge_rotate", text="Rotate CW").use_ccw = False
        col.operator("mesh.edge_rotate", text="Rotate CCW").use_ccw = True


classes = (
    MESH_MT_PIE_symmetrize,
    PIE_MT_edge_menu,
)
