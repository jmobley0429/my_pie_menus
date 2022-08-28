import bpy
from bpy.types import Menu


class IMAGE_MT_uvs_snap_pie_custom(Menu):
    bl_label = "Snap"
    bl_idname = "IMAGE_MT_uvs_snap_pie_custom"

    def draw(self, _context):
        import string

        layout = self.layout
        pie = layout.menu_pie()

        layout.operator_context = 'EXEC_REGION_WIN'

        pie.operator(
            "uv.snap_selected",
            text="Selected to Pixels",
            icon='RESTRICT_SELECT_OFF',
        ).target = 'PIXELS'
        pie.operator(
            "uv.snap_cursor",
            text="Cursor to Pixels",
            icon='PIVOT_CURSOR',
        ).target = 'PIXELS'
        pie.operator(
            "uv.snap_cursor",
            text="Cursor to Selected",
            icon='PIVOT_CURSOR',
        ).target = 'SELECTED'
        col = pie.column()
        col.label(text="Snap to Midpoint")
        for ax in list("xy"):
            spl = col.split()
            for side in "MIN MAX".split():
                label = f"{ax.capitalize()} - {string.capwords(side)}"
                op = spl.operator('uv.snap_uvs_to_midpoint', text=label)
                op.direction = ax
                op.bounds = side
        pie.operator(
            "uv.snap_selected",
            text="Selected to Cursor",
            icon='RESTRICT_SELECT_OFF',
        ).target = 'CURSOR'
        pie.operator(
            "uv.snap_selected",
            text="Selected to Cursor (Offset)",
            icon='RESTRICT_SELECT_OFF',
        ).target = 'CURSOR_OFFSET'
        pie.operator(
            "uv.snap_selected",
            text="Selected to Adjacent Unselected",
            icon='RESTRICT_SELECT_OFF',
        ).target = 'ADJACENT_UNSELECTED'
        pie.operator(
            "uv.snap_cursor",
            text="Cursor to Origin",
            icon='PIVOT_CURSOR',
        ).target = 'ORIGIN'


class PIE_MT_UVUnwrapPie(Menu):
    bl_idname = "PIE_MT_UVUnwrapPie"
    bl_label = "UV Unwrap Pie"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.uvp2_props
        pie = layout.menu_pie()
        # L
        pie.operator("uv.pack_with_mode", text="Pack")
        # R
        pie.operator("uv.textools_rectify")
        # B
        pie.operator('uv.seams_from_islands', text="Island Seams")
        # T
        pie.operator('uv.toggle_uv_sync_selection')
        col = pie.column()
        col.label(text="Unwrap")
        col.scale_x = 0.9
        spl = col.split()
        spl.operator("uv.pin", text="Pin")
        spl.operator("uv.pin", text="Unpin").clear = True
        spl = col.split(factor=0.5, align=True)
        spl.operator("uv.unwrap", text="Unwrap")
        row = spl.row(align=True)
        row.operator("uv.textools_uv_unwrap", text="U").axis = "x"
        row.operator("uv.textools_uv_unwrap", text="V").axis = "y"

        col = pie.column()
        col.label(text="Add to Lock Groups")
        col.scale_x = 1
        spl = col.split()
        spl.operator("uvpackmaster2.set_free_island_lock_group", text="Current")
        spl.operator("uvpackmaster2.set_island_lock_group", text="Free")
        spl = col.split()
        spl.prop(props, "lock_groups_enable", text="Enable")
        col = pie.column()
        col.scale_x = 0.8
        spl = col.split()
        col.label(text="Pixel Spacing")
        row = col.row(align=True)
        row.prop(props, "pixel_margin", text="Margin")
        row = col.row(align=True)
        row.prop(props, "pixel_padding", text="Padding")
        row = col.row(align=True)
        row.prop(props, "pixel_margin_tex_size", text="Tex. Size")
        col = pie.column()
        col.scale_x = 0.9
        spl = col.split()
        col.label(text="Transform")
        spl = col.split()
        spl.operator("uv.textools_uv_crop")
        spl.operator("uv.textools_uv_fill")
        spl = col.split()
        spl.operator("uv.textools_island_align_edge", text="Align Edge")
        spl.operator("uv.textools_island_align_world", text="Align World")


classes = (
    PIE_MT_UVUnwrapPie,
    IMAGE_MT_uvs_snap_pie_custom,
)
