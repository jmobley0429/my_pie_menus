import bpy
from bpy.types import Menu


class OBJECT_MT_smooth_shading_menu(Menu):
    bl_idname = "OBJECT_MT_smooth_shading_menu"
    bl_label = "Smooth Shading"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        obj = context.object
        me = obj.data

        layout = self.layout
        col = layout.column(align=False, heading="Auto Smooth")
        col.use_property_decorate = False
        row = col.row(align=True)
        sub = row.row(align=True)
        sub.prop(mesh, "use_auto_smooth", text="")
        sub = sub.row(align=True)
        sub.active = mesh.use_auto_smooth and not mesh.has_custom_normals
        sub.prop(mesh, "auto_smooth_angle", text="")
        row.prop_decorator(mesh, "auto_smooth_angle")
        if me.has_custom_normals:
            col.operator("mesh.customdata_custom_splitnormals_clear", icon='X')
        else:
            col.operator("mesh.customdata_custom_splitnormals_add", icon='ADD')


from my_pie_menus import utils


kms = []


def register():

    utils.register_classes(classes)
    utils.register_keymaps(kms)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        utils.unregister_keymaps(kms)
