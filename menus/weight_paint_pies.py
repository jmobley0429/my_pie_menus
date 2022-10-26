import bpy


class PIE_MT_WeightPaintPie(bpy.types.Menu):
    bl_idname = "PIE_MT_WeightPaintPie"
    bl_label = "Weigh Paint Pie"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        op = pie.operator("weight_paint.set_brush", text="Add")
        op.brush_type = "Draw"
        op.draw_brush_type = "Add"

        op = pie.operator("weight_paint.set_brush", text="Subtract")
        op.brush_type = "Draw"
        op.draw_brush_type = "Subtract"

        col = pie.column()
        op = col.operator(
            "weight_paint.set_brush",
            text="Multiply",
        )
        op.brush_type = "Draw"
        op.draw_brush_type = "Multiply"

        op = col.operator("weight_paint.set_brush", text="Darken")
        op.brush_type = "Draw"
        op.draw_brush_type = "Darken"

        op = col.operator("weight_paint.set_brush", text="Lighten")
        op.brush_type = "Draw"
        op.draw_brush_type = "Lighten"

        op = pie.operator("weight_paint.set_brush", text="Smear")
        op.brush_type = "Smear"

        op = pie.operator("weight_paint.set_brush", text="Average")
        op.brush_type = "Average"

        op = pie.operator("weight_paint.set_brush", text="Gradient")
        op.brush_type = "gradient"

        op = pie.operator("weight_paint.set_brush", text="Blur")
        op.brush_type = "Blur"


classes = [
    PIE_MT_WeightPaintPie,
]

kms = [
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Weight Paint",
        "letter": "W",
        "shift": 1,
        "ctrl": 0,
        "alt": 0,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_WeightPaintPie"},
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
