bl_info = {
    "name": "Random Vertex Color Per Object",
    "author": "Jake Mobley",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "F3 Menu > Search 'Random Vertex Color Per Object'",
    "description": "Generate Random Vertex Color Per Object",
    "warning": "",
    "doc_url": "",
    "category": "Object",
    'internet':'',
}


import bpy
import numpy as np


def generate_random_v_colors_per_obj(context, **args):
    multi_obj = args.pop("multi_obj")
    objs = context.selected_objects[:]
    colors = []
    margin = 0.03

    def generate_color():
        too_close = False
        color = np.random.random_sample((3,))
        color = np.append(color, 1.0)
        for col in colors:
            col_avg = np.mean(col)
            new_col_avg = np.mean(color)
            diff = col_avg - new_col_avg
            if abs(diff) < margin:
                too_close = True
        if not too_close:
            colors.append(color)
            return color
        return generate_color()

    if not multi_obj:
        color = generate_color()

    for obj in objs:
        if obj.type == "MESH":
            mesh = obj.data
            vcol = mesh.vertex_colors
            color_layer = vcol["Col"] if vcol else vcol.new()
            if multi_obj:
                color = generate_color()
            i = 0
            for poly in mesh.polygons[:]:
                for loop in poly.loop_indices:
                    color_layer.data[i].color = color
                    i += 1


class OBJECT_OT_generate_random_v_colors_per_obj(bpy.types.Operator):
    bl_idname = "object.generate_random_v_colors_per_obj"
    bl_label = "Random Vertex Color Per Object"
    bl_options = {"REGISTER", "UNDO"}

    multi_obj: bpy.props.BoolProperty(
        default=True,
        name="Multi Object",
        description="multi_obj: True, Give each selected object it's own random color. False: Set all objects to one color",
    )

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.selected_objects

    def execute(self, context):
        args = self.as_keywords()
        generate_random_v_colors_per_obj(context, **args)
        return {"FINISHED"}


def register():
    bpy.utils.register_class(OBJECT_OT_generate_random_v_colors_per_obj)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_generate_random_v_colors_per_obj)


if __name__ == "__main__":
    print("***\n" * 5)
    print("REGISTERING")
    print("***\n" * 5)
    register()
