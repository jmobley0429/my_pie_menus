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
        # Right -- Bevel
        box = pie.split().column()
        box.operator('object.custom_bevel_modifier', text="Bevel", icon="MOD_BEVEL")
        box.operator('object.custom_bevel_subsurf_modifier', text="Bevel Subsurf", icon="MOD_SUBSURF")
