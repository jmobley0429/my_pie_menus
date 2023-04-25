import bpy
from bpy.types import Menu, Operator
import numpy as np
from ..operators.edit_mode_operators import *


class MESH_MT_PIE_symmetrize(Menu):
    bl_label = "Select Mode"
    bl_idname = "MESH_MT_PIE_symmetrize"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator_enum("mesh.symmetrize", "direction")


class MESH_MT_edge_menu(Menu):
    # label is displayed at the center of the pie menu.
    bl_idname = "MESH_MT_edge_menu"
    bl_label = "Edge Menu"
    bl_options = {"REGISTER", "UNDO"}

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
        row = col.row(align=True)
        row.operator("mesh.subdivide_inner_edges")
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
        col.operator("mesh.reduce_cylinder")
        col.operator("mesh.reduce_circle_segments")
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
        col.ui_units_x += 5 
        row = col.row(align=True)
        row.operator("mesh.edge_split")
        row = col.row(align=True)
        spl = row.split()
        spl.operator("mesh.edge_rotate", text="Rotate CW").use_ccw = False
        spl.operator("mesh.edge_rotate", text="CCW").use_ccw = True
        row = col.row(align=True)
        row.operator("mesh.offset_edge_loops_slide")
       


class MESH_MT_face_menu(Menu):
    # label is displayed at the center of the pie menu.
    bl_idname = "MESH_MT_face_menu"
    bl_label = "Face Pie Menu"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # Left

        op = pie.operator("mesh.faces_select_linked_flat")
        op.sharpness = np.radians(25)
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
        pie.operator_context = "INVOKE_REGION_WIN"
        pie.operator("mesh.smart_grid_fill")


class MESH_MT_merge_verts_pie(Menu):
    bl_idname = 'MESH_MT_merge_verts_pie'
    bl_label = "Merge Verts"
    bl_options = {"REGISTER", "UNDO"}

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


class MESH_OT_gstretch_override(Operator):
    bl_label = "GStretch"
    bl_idname = "mesh.custom_gstretch"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.types.MESH_OT_looptools_gstretch.poll(context)

    def execute(self, context):
        bpy.ops.mesh.looptools_gstretch()
        bpy.ops.remove.annotation()
        return {"FINISHED"}


class MESH_MT_PIE_loop_tools(Menu):
    bl_label = "Loop Tools"
    bl_idname = "MESH_MT_PIE_loop_tools"
    bl_options = {"REGISTER", "UNDO"}

    

    def draw(self, context):
        layout = self.layout
        context.window_manager.looptools.gstretch_use_guide = "Annotation"
        pie = layout.menu_pie()
        op = pie.operator("mesh.looptools_bridge")
        op = pie.operator("mesh.looptools_circle")
        op = pie.operator("mesh.looptools_curve")
        op = pie.operator("mesh.looptools_flatten")
        op = pie.operator("mesh.custom_gstretch")
        op = pie.operator("mesh.looptools_loft")
        op = pie.operator("mesh.looptools_relax")
        op = pie.operator("mesh.looptools_space")


class MESH_MT_PIE_select_by_trait(Menu):
    bl_label = "Select by Trait"
    bl_idname = "MESH_MT_PIE_select_by_trait"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("mesh.select_face_by_sides")
        pie.operator("mesh.select_interior_faces")
        pie.operator("mesh.select_loose")
        pie.operator("mesh.select_non_manifold")
        pie.operator(MESH_OT_cleanup_select_ngons.bl_idname)
        pie.operator(MESH_OT_cleanup_select_short_edges.bl_idname)
        pie.operator(MESH_OT_cleanup_select_small_faces.bl_idname)
        pie.operator(MESH_OT_cleanup_handle_ngons.bl_idname)


class MESH_MT_PIE_cleanup(Menu):
    bl_label = "Clean Up Pie"
    bl_idname = "MESH_MT_PIE_cleanup"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        op = pie.operator("mesh.delete_loose")
        op = pie.operator("mesh.decimate")
        op.ratio = 0.1
        op = pie.operator("mesh.dissolve_degenerate")
        op = pie.operator("mesh.face_make_planar")
        op = pie.operator("mesh.vert_connect_nonplanar")
        op = pie.operator("mesh.vert_connect_concave")


classes = (
    MESH_OT_gstretch_override,
    MESH_MT_PIE_symmetrize,
    MESH_MT_edge_menu,
    MESH_MT_merge_verts_pie,
    MESH_MT_PIE_loop_tools,
    MESH_MT_face_menu,
    MESH_MT_PIE_select_by_trait,
    MESH_MT_PIE_cleanup,
)

kms = [
    
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "Q",
        "shift": True,
        "ctrl": False,
        "alt": False,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "MESH_MT_PIE_symmetrize"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "E",
        "shift": True,
        "ctrl": True,
        "alt": False,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "MESH_MT_edge_menu"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "F",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "MESH_MT_face_menu"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "W",
        "shift": 1,
        "ctrl": 0,
        "alt": 0,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "MESH_MT_merge_verts_pie"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "TWO",
        "shift": 0,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "MESH_MT_PIE_select_by_trait"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "THREE",
        "shift": 0,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "MESH_MT_PIE_cleanup"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "ONE",
        "shift": False,
        "ctrl": False,
        "alt": True,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "MESH_MT_PIE_loop_tools"},
    },
]

from my_pie_menus import utils

addon_keymaps = []


def register():

    utils.register_classes(classes)
    utils.register_keymaps(kms, addon_keymaps)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        utils.unregister_keymaps(kms)
