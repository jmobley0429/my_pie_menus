import bpy


class Brush:
    def __init__(self, context):
        self.context = context
        self.mode = context.mode
        self.ts = context.tool_settings

        BRUSH_ATTRIBUTES = {
            "SCULPT": {
                "brush": self.ts.sculpt.brush,
                "settings": self.ts.sculpt.brush,
                "ss_attr": "use_smooth_stroke",
                "ss_radius_attr": "smooth_stroke_radius",
            },
            "PAINT_GPENCIL": {
                "brush": self.ts.gpencil_paint.brush,
                "settings": self.ts.gpencil_paint.brush.gpencil_settings,
                "ss_attr": "use_settings_stabilizer",
                "ss_radius": "use_settings_stabilizer",
            },
        }
        self.brush_attrs = BRUSH_ATTRIBUTES[self.mode]

    @property
    def brush(self):
        return self.brush_attrs["brush"]

    @property
    def settings(self):
        return self.brush_attrs["settings"]

    @property
    def ss_attr(self):
        return self.brush_attrs["ss_attr"]

    @property
    def use_smooth_stroke(self):
        attr = self.brush_attrs["ss_attr"]
        return getattr(self.settings, attr)


class BRUSH_OT_toggle_stabilize_stroke(bpy.types.Operator):

    bl_idname = "brush.toggle_stabilize_stroke"
    bl_label = "Toggle Stabilize Stroke"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode in {"SCULPT", "PAINT_GPENCIL"}

    def execute(self, context):
        br = Brush(context)
        settings = br.brush
        attr = br.ss_attr
        setattr(settings, attr, not br.use_smooth_stroke)
        return {'FINISHED'}


class BRUSH_OT_adjust_stabilize_radius(bpy.types.Operator):

    bl_idname = "brush.adjust_stabilize_radius"
    bl_label = "Adjust Stabilize Stroke Radius"
    bl_options = {"REGISTER", "UNDO"}

    radius: bpy.props.IntProperty(name="Smooth Stroke Radius")

    @classmethod
    def poll(cls, context):
        cls.br = Brush(context)
        mode = context.mode in {"SCULPT", "PAINT_GPENCIL"}
        use_ss = cls.br.use_smooth_stroke
        return all([mode, use_ss])

    def invoke(self, context, event):
        self.brush = self.br.brush
        self.radius = self.brush.smooth_stroke_radius
        return context.window_manager.invoke_props_popup(self, event)

    def execute(self, context):
        self.brush.smooth_stroke_radius = self.radius
        return {'FINISHED'}


classes = [
    BRUSH_OT_toggle_stabilize_stroke,
    BRUSH_OT_adjust_stabilize_radius,
]
