from my_pie_menus.resources import utils
import bpy

from .custom_operator import (
    CustomOperator,
    CustomModalOperator,
    CustomBmeshOperator,
    OperatorBaseClass,
)

class WINDOW_OT_switch_to_workspace(bpy.types.Operator):
    
    bl_idname = "wm.switch_to_workspace"
    bl_description = 'Switch to selected workspace view.'
    bl_label = "Switch to Workspace"
    bl_options = {"REGISTER"}

    ws_type: bpy.props.EnumProperty(
        items=[
        ( "Animation", "Animation",  "Animation"),
        ( "Asset Browser", "Asset Browser",  "Asset Browser"),
        ( "Compositing", "Compositing",  "Compositing"),
        ( "Geometry Nodes", "Geometry Nodes",  "Geometry Nodes"),
        ( "Modeling", "Modeling",  "Modeling"),
        ( "Scripting", "Scripting",  "Scripting"),
        ( "Shading", "Shading",  "Shading"),
        ( "UV Editing", "UV Editing",  "UV Editing"),
        ]
    )

    def get_workspace(self):
        try:
            ws = bpy.data.workspaces[self.ws_type]
            return ws 
        except KeyError:
            return 

    def execute(self, context):
        ws = self.get_workspace()
        if ws is None:
            self.report({"ERROR"}, "Cannot find {self.ws_type} in available workspaces.")
            return {"CANCELLED"}
        context.window.workspace = ws
        return {"FINISHED"}
    
classes = [
    WINDOW_OT_switch_to_workspace
]

def register():
    utils.register_classes(classes)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)