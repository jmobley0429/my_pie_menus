import bpy
import blf
import bmesh


class CustomOperator:
    # @classmethod
    # def poll(cls, context):
    #     return context.active_object is not None

    @staticmethod
    def get_active_obj():
        return bpy.context.active_object

    @staticmethod
    def get_selected_objects():
        return bpy.context.selected_objects

    @staticmethod
    def get_last_added_object():
        return bpy.context.object

    @staticmethod
    def edit_obj_poll(context):
        return context.mode == "EDIT_MESH" and context.active_object is not None

    def to_mode(self, mode):
        bpy.ops.object.mode_set(mode=mode)

    def get_mod_and_target_objects(self):
        target = self.get_active_obj()
        objs = set(self.get_selected_objects())
        mod = list(objs - {target})[0]
        return (mod, target)

    def close_modifiers(self):
        obj = self.get_active_obj()
        modifiers = obj.modifiers[:]
        for mod in modifiers:
            mod.show_expanded = False

    def _get_last_modifier(self):
        obj = self.get_active_obj()
        return obj.modifiers[:][-1]

    @property
    def last_constraint(obj):
        return obj.constraints[0]

    def set_active_and_selected(self, context, obj, selected=True):
        context.view_layer.objects.active = obj
        obj.select_set(selected)

    def select_objects_in_list(self, obj_list):
        for obj in obj_list:
            obj.select_set(True)


class CustomModalOperator(CustomOperator):
    mod_name: bpy.props.StringProperty()
    initial_mouse: bpy.props.IntProperty()

    wheel_input = {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}

    numpad_input = {
        "NUMPAD_2",
        "NUMPAD_4",
        "NUMPAD_6",
        "NUMPAD_8",
        "NUMPAD_1",
        "NUMPAD_3",
        "NUMPAD_5",
        "NUMPAD_7",
        "NUMPAD_9",
        "NUMPAD_0",
        "NUMPAD_ENTER",
        "BACK_SPACE",
        "NUMPAD_PERIOD",
    }
    numpad_value = []

    @property
    def modifier(self):
        obj = self.get_active_obj()
        return obj.modifiers[self.mod_name]

    def exit_modal(self, context, cancelled=False):
        context.area.header_text_set(None)
        self.close_modifiers()
        if cancelled:
            return {'CANCELLED'}
        return {'FINISHED'}

    @property
    def string_numpad_value(self):
        return ''.join(self.numpad_value)

    @property
    def float_numpad_value(self):
        return float(self.string_numpad_value)

    @property
    def int_numpad_value(self):
        return int(self.string_numpad_value)

    def display_modal_info(self, msg, context):
        '''Takes a string of info for the
        modal and displays it in the UI Header'''
        if self.numpad_value:
            msg += f" Input : {self.string_numpad_value}"
        context.area.header_text_set(msg)

    def _clear_info(self, context):
        context.area.header_text_set(None)


class CustomBmeshOperator(CustomOperator):
    @classmethod
    def bmesh(cls, context):
        cls.me = context.edit_object.data
        bm = bmesh.from_edit_mesh(cls.me)
        cls.bm = bm

    @classmethod
    def new_bmesh(cls, mesh_name):
        mesh = bpy.data.meshes.new(mesh_name)
        return bmesh.new()

    @property
    def sel_edges(self):
        return [e for e in self.bm.edges[:] if e.select]

    @staticmethod
    def is_vert(element):
        return isinstance(element, bmesh.types.BMVert)

    @staticmethod
    def is_edge(element):
        return isinstance(element, bmesh.types.BMEdge)

    @staticmethod
    def is_face(element):
        return isinstance(element, bmesh.types.BMFace)

    def select_sharp_edges(self, bm, threshold):
        for edge in bm.edges[:]:
            angle = edge.calc_face_angle()
            if angle >= threshold:
                edge.select = True
            else:
                edge.select = False

    def select_edges(self, context, edges, select=True):
        try:
            for edge in edges:
                edge.select = select
        except ReferenceError:
            self.bmesh(context)
            self.select_edges(context, edges, select=select)


class ModalDrawText:
    def __init__(self, context, msg):
        self.msg = msg
        self.handle = bpy.types.SpaceView3D.draw_handler_add(
            self.draw_text_callback, (context,), 'WINDOW', 'POST_PIXEL'
        )

    def draw_text_callback(self, context):
        font_id = 0
        # draw some text
        blf.position(font_id, 15, 50, 0)
        blf.size(font_id, 20, 72)
        blf.draw(font_id, "%s" % (self.msg))

    def remove_handle(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')


classes = [CustomOperator, CustomModalOperator]
