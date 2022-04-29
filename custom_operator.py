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
