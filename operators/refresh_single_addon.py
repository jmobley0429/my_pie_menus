bl_info = {
    "name": "Refresh Single Addon",
    "description": "Refresh one addon with builtin register function",
    "author": "Jake Mobley",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "Text Editor > N Panel",
    "category": "Text Editor",
}

import bpy


class RefreshAddonProps(bpy.types.PropertyGroup):
    refresh_addon_filepath: bpy.props.StringProperty(
        name="File Path",
        default='/home/jake/blender/projects/scripts/',
        subtype="FILE_PATH",
    )
    refresh_addon_module_name: bpy.props.StringProperty(name="Module Name")


class PREFS_OT_refresh_single_addon(bpy.types.Operator):
    """Refresh single addon with built-in register function."""

    bl_idname = "preferences.refresh_single_addon"
    bl_label = "Refresh Single Addon"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        props = context.window_manager.refresh_props
        bpy.ops.preferences.addon_remove(module=props.refresh_addon_module_name)
        print("###" * 3)
        print(props.refresh_addon_filepath)
        bpy.ops.preferences.addon_install(filepath=props.refresh_addon_filepath)
        bpy.ops.preferences.addon_enable(module=props.refresh_addon_module_name)
        return {'FINISHED'}


class TEXT_PT_RefreshSingleAddonPanel(bpy.types.Panel):
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_label = "Refresh Single Addon"
    bl_category = "Text"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        props = context.window_manager.refresh_props
        layout.prop(props, 'refresh_addon_filepath')
        layout.prop(props, 'refresh_addon_module_name')
        op = layout.operator("preferences.refresh_single_addon")


def register():
    bpy.utils.register_class(RefreshAddonProps)
    bpy.types.WindowManager.refresh_props = bpy.props.PointerProperty(type=RefreshAddonProps)
    bpy.utils.register_class(PREFS_OT_refresh_single_addon)
    bpy.utils.register_class(TEXT_PT_RefreshSingleAddonPanel)


def unregister():
    bpy.utils.unregister_class(PREFS_OT_refresh_single_addon)
    bpy.utils.unregister_class(TEXT_PT_RefreshSingleAddonPanel)
    bpy.utils.unregister_class(RefreshAddonProps)
    del bpy.types.WindowManager.refresh_props


if __name__ == "__main__":
    register()
