import bpy


class ToggleStabilizeStroke(bpy.types.Operator):

    bl_idname = "sculpt.toggle_stabilize_stroke"
    bl_label = "Toggle Stabilize Stroke"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == "SCULPT"

    def execute(self, context):
        brush = context.tool_settings.sculpt.brush
        val = brush.use_smooth_stroke
        brush.use_smooth_stroke = not val
        return {'FINISHED'}


class AdjustStabilizeStrokeRadius(bpy.types.Operator):

    bl_idname = "sculpt.adjust_ss_radius"
    bl_label = "Adjust Stabilize Stroke Radius"
    bl_options = {"REGISTER", "UNDO"}

    radius: bpy.props.IntProperty(name="Smooth Stroke Radius")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        mode = context.mode
        brush = context.tool_settings.sculpt.brush
        return obj is not None and mode == "SCULPT" and brush.use_smooth_stroke == True

    def invoke(self, context, event):
        self.radius = context.tool_settings.sculpt.brush.smooth_stroke_radius
        return context.window_manager.invoke_props_popup(self, event)

    def execute(self, context):
        self.change_radius(context)
        return {'FINISHED'}

    def change_radius(self, context):
        brush = context.tool_settings.sculpt.brush
        brush.smooth_stroke_radius = self.radius


classes = [
    ToggleStabilizeStroke,
    AdjustStabilizeStrokeRadius,
]
