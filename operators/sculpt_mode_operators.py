import bpy
import json
from pathlib import Path
from .custom_operator import CustomModalOperator

ROOT = Path(__file__).parent.parent.resolve()
custom_shape_fp = ROOT.joinpath('resources', 'gizmo_circle_mesh.json')


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


#
# class BRUSH_GT_stabilize_stroke_radius(Gizmo):
#     bl_idname = "VIEW3D_GT_ss_radius_widget"
#     bl_target_properties = ({"id": "radius", "type": 'FLOAT', "array_length": 1},)
#
#     __slots__ = (
#         "custom_shape",
#         "init_mouse_y",
#         "init_value",
#     )
#     with open(custom_shape_fp, 'r') as f:
#         custom_shape_verts = json.load(f)
#
#     # def _update_offset_matrix(self):
#     #     # offset behind the light
#     #     self.matrix_offset.col[3][2] = self.target_get_value("offset") / -10.0
#
#     def draw(self, context):
#         # self._update_offset_matrix()
#         self.draw_custom_shape(self.custom_shape)
#
#     def draw_select(self, context, select_id):
#         # self._update_offset_matrix()
#         self.draw_custom_shape(self.custom_shape, select_id=select_id)
#
#     def setup(self):
#         if not hasattr(self, "custom_shape"):
#             self.custom_shape = self.new_custom_shape('LINES', self.custom_shape_verts)
#
#     def invoke(self, context, event):
#         self.init_mouse_x = event.mouse_x
#         self.init_value = self.target_get_value("radius")
#         return {'RUNNING_MODAL'}
#
#     def exit(self, context, cancel):
#         context.area.header_text_set(None)
#         if cancel:
#             self.target_set_value("radius", self.init_value)
#
#     def modal(self, context, event, tweak):
#         delta = (event.mouse_x - self.init_mouse_x) / 10.0
#         if 'SNAP' in tweak:
#             delta = round(delta)
#         if 'PRECISE' in tweak:
#             delta /= 10.0
#         value = self.init_value - delta
#         self.target_set_value("radius", value)
#         context.area.header_text_set("SMOOTH STROKE RADIUS: %.4f" % value)
#         return {'RUNNING_MODAL'}
#
#
# class BRUSH_GGT_stabilize_stroke_radius(GizmoGroup):
#     bl_idname = "BRUSH_GGT_ss_radius"
#     bl_label = "Stabilize Stroke Radius"
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'WINDOW'
#     bl_options = {'3D', 'PERSISTENT'}
#
#     @classmethod
#     def poll(cls, context):
#         op = cls.my_target_operator(context)
#         if op is None:
#             wm = context.window_manager
#             wm.gizmo_group_type_unlink_delayed(BRUSH_GGT_stabilize_stroke_radius.bl_idname)
#             return False
#         return True
#
#     def move_get_cb():
#         op = BRUSH_GGT_stabilize_stroke_radius.my_target_operator(context)
#         return op.radius
#
#     def move_set_cb(value):
#         op = BRUSH_GGT_stabilize_stroke_radius.my_target_operator(context)
#         op.radius = value
#         # XXX, this may change!
#         op.execute(context)
#
#     @staticmethod
#     def my_target_operator(context):
#         wm = context.window_manager
#         op = wm.operators[-1] if wm.operators else None
#         if isinstance(op, BRUSH_OT_adjust_stabilize_radius):
#             return op
#         return None
#
#     def setup(self, context):
#         # Assign the 'offset' target property to the light energy.
#         wm = context.window_manager
#         gz = self.gizmos.new(BRUSH_GT_stabilize_stroke_radius.bl_idname)
#         gz.target_set_prop("radius", wm.StrokeSettings, "radius")
#         gz.target_set_handler("offset", get=move_get_cb, set=move_set_cb)
#         gz.color = 0.5, 0.5, 1.0
#         gz.alpha = 0.5
#         gz.scale_basis = 0.2
#         gz.use_draw_modal = True
#         self.radius_gizmo = gz
#
#         # def size_get(self, )


class BRUSH_OT_adjust_stabilize_radius(CustomModalOperator, bpy.types.Operator):

    bl_idname = "brush.adjust_stabilize_radius"
    bl_label = "Adjust Stabilize Stroke Radius"
    bl_options = {"REGISTER", "UNDO"}

    radius: bpy.props.FloatProperty(name="Smooth Stroke Radius")

    @classmethod
    def poll(cls, context):
        mode = context.mode in {"SCULPT", "PAINT_GPENCIL"}
        if not mode:
            return False
        cls.br = Brush(context)
        use_ss = cls.br.use_smooth_stroke
        return all([mode, use_ss])

    def invoke(self, context, event):
        self.brush = self.br.brush
        self.radius = self.brush.smooth_stroke_radius
        self.init_mouse_x = event.mouse_x

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        msg = f"SMOOTH STROKE RADIUS: {self.radius:.2f}"
        self.display_modal_info(msg, context)
        modifier = 0.1
        delta = 0
        if event.shift:
            modifier = 0.01
        if event.type == "MOUSEMOVE":
            delta = self.init_mouse_x - event.mouse_x
            delta *= modifier
            self.init_mouse_x = event.mouse_x
        elif event.type in {"RIGHTMOUSE", "ESC"}:
            return self.exit_modal(context, cancelled=True)
        elif event.type == "LEFTMOUSE":
            self.brush.smooth_stroke_radius = int(self.radius)
            return self.exit_modal(context)
        print(delta)
        self.radius -= delta
        return {"RUNNING_MODAL"}


classes = [
    BRUSH_OT_toggle_stabilize_stroke,
    BRUSH_OT_adjust_stabilize_radius,
]
