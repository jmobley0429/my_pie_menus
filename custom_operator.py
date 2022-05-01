import bpy


class CustomOperator:
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    @staticmethod
    def get_active_obj():
        return bpy.context.active_object

    @staticmethod
    def get_selected_objects():
        return bpy.context.selected_objects

    @staticmethod
    def get_last_added_object():
        return bpy.context.scene.objects[:][-1]

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


class CustomModalOperator(CustomOperator):
    mod_name: bpy.props.StringProperty()
    initial_mouse: bpy.props.IntProperty()

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
