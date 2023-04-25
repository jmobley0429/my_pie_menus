import bpy
import blf
import bmesh


class CustomOperator:
    # @classmethod
    # def poll(cls, context):
    #     return context.active_object is not None

    def _set_args(self, args):
        if args:
            for key, value in args.items():
                setattr(self, key, value)

    def get_current_mode(self, context):
        if "EDIT" in context.mode:
            return "EDIT"
        elif "SCULPT" in context.mode:
            return "SCULPT"
        return None

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
        if "EDIT" not in context.mode:
            return False
        if context.active_object is None:
            return False
        if context.active_object.type != "MESH":
            return False
        return True
      

    def to_mode(self, mode):
        bpy.ops.object.mode_set(mode=mode)

    def in_mode(self, context, mode):
        return mode in context.mode

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

    def set_numpad_input(self, event):
        if event.type == "BACKSPACE":
            self.numpad_value.pop()
        else:
            self.numpad_value.append(event.ascii)

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
            inp_msg = f", Input : {self.string_numpad_value}"
        else:
            inp_msg = ''
        context.area.header_text_set(msg + inp_msg)

    def _clear_info(self, context):
        context.area.header_text_set(None)


class CustomBmeshOperator(CustomOperator):
    
    @classmethod
    def bmesh(cls, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")
        obj = context.active_object
        cls.mesh = obj.data
        bm = bmesh.from_edit_mesh(cls.mesh)
        cls.bm = bm

    @classmethod
    def new_bmesh(cls, mesh_name):
        cls.mesh = bpy.data.meshes.new(mesh_name)
        cls.bm = bmesh.new()
        cls.bm.from_mesh(cls.mesh)

    @staticmethod
    def select_elem_in_list(all_elements, in_list):
        for elem in all_elements:
            if elem not in in_list:
                elem.select_set(False)
            else:
                elem.select_set(True)
    
    def cleanup_bmesh(self):
        self.bm.free()

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

    def select_sharp_edges(self, threshold):
        if self.bm:
            for edge in self.bm.edges[:]:
                try:
                    angle = edge.calc_face_angle()
                except ValueError:
                    angle = None
                if angle is not None and angle >= threshold:
                    edge.select = True
                else:
                    edge.select = False

    @staticmethod
    def is_boundary_edge(edge):
        num_faces = len(list(filter(lambda face: face.select, edge.link_faces[:])))
        return num_faces == 1

    def select_edges(self, context, edges, select=True, skip_callback_func=None):
        try:
            for edge in edges:
                edge.select = select
                if skip_callback_func is not None:
                    if skip_callback_func(edge):
                        edge.select = not select

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


bl_info = {
    "name": "Set Shade Auto Smooth",
    "author": "X Y",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D",
    "description": "Set Shade Auto Smooth with one Click",
    "category": "Object",
}

import bpy


class OBJECT_OT_shade_auto_smooth(bpy.types.Operator):
    bl_idname = "object.shade_auto_smooth"
    bl_label = "Shade Auto Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    # put checking for object type and correct context
    # in the poll method rather than execute.
    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type in {"MESH", "CURVE"}

    def execute(self, context):
        # allows for use in edit mode and object mode alike.
        in_edit = 'EDIT' in context.mode
        if in_edit:
            bpy.ops.object.mode_set(mode="OBJECT")
        # using one operator call to act on all selected objects
        # rather than looping over every polygon
        bpy.ops.object.shade_smooth()
        for obj in context.selected_objects:
            if obj.type == "MESH":
                obj.data.use_auto_smooth = True
        if in_edit:
            bpy.ops.object.mode_set(mode="EDIT")
        return {'FINISHED'}

class OperatorBaseClass(CustomOperator):
    
    def __init__(self, context, args=None, op=None):
        self.context = context
        if args is not None:
            self._set_args(args)
        if op is not None:
            self.op = op

class EditModeOperatorBaseClass(OperatorBaseClass, CustomBmeshOperator):

    def __init__(self, context, args=None, op=None):
        super().__init__(context, args, op=op)

    


def register():
    bpy.utils.register_class(OBJECT_OT_shade_auto_smooth)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_shade_auto_smooth)


if __name__ == "__main__":
    register()
