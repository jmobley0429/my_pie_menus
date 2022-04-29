import bpy
from bpy.types import Menu


class PIE_MT_AddModifier(Menu):
    bl_idname = "PIE_MT_AddModifier"
    bl_label = "Pie Add Modifier"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type != 'GPENCIL'

    def _draw_mirror_submenu(self, layout):
        ''' '''

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Left -- Mirror
        pie = layout.menu_pie()
        box = pie.split().column()
        op = box.operator('object.custom_mirror_modifier', text="Mirror X", icon="MOD_MIRROR")
        op.mirror_type = "X"
        op = box.operator('object.custom_mirror_modifier', text="Mirror Y", icon="MOD_MIRROR")
        op.mirror_type = "Y"
        op = box.operator('object.custom_mirror_modifier', text="Mirror Z", icon="MOD_MIRROR")
        op.mirror_type = "Z"
        # Right -- Bevel / Shading
        box = pie.split().column()
        box.operator('object.custom_bevel_modifier', text="Bevel", icon="MOD_BEVEL")
        box.operator('object.custom_bevel_subsurf_modifier', text="Bevel Subsurf", icon="MOD_SUBSURF")
        op = box.operator('object.modifier_add', text="Weighted Normal", icon="MOD_NORMALEDIT")
        op.type = "WEIGHTED_NORMAL"
        # Bottom -- Deform
        box = pie.split().column()
        box.operator("object.custom_simple_deform", text="Bend", icon="MOD_SIMPLEDEFORM")
        box.operator("object.custom_shrinkwrap", text="Shrinkwrap", icon="MOD_SHRINKWRAP")
        box.operator("object.custom_lattice", text="Lattice", icon="OUTLINER_DATA_LATTICE")
        # Top -- Mesh \ Edges
        box = pie.split().column()
        box.operator("object.custom_remesh", text="Remesh", icon="MOD_REMESH")
        box.operator("object.custom_decimate", text="Decimate", icon="MOD_DECIM")
        op = box.operator("object.modifier_add", text="Wireframe", icon="MOD_WIREFRAME")
        op.type = "WIREFRAME"
