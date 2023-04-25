import bpy
import numpy as np
from mathutils import Vector


class NODE_OT_directional_node_align(bpy.types.Operator):
    bl_idname = "node.directional_align"
    bl_label = "Align Nodes"
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.EnumProperty(
        items=(
            ("TOP", "Top", "Top"),
            ("BOTTOM", "Bottom", "Bottom"),
            ("LEFT", "Left", "Left"),
            ("RIGHT", "Right", "Right"),
        ),
        name='Direction',
        description='Direction to align on.',
        default=None,
    )

    @classmethod
    def poll(cls, context):
        return context.area.type == "NODE_EDITOR" and bool(context.selected_nodes)

    def execute(self, context):
        sel_nodes = context.selected_nodes
        axis = "y" if self.direction in {"TOP", "BOTTOM"} else "x"
        min_max_func = min if self.direction in {"LEFT", "BOTTOM"} else max
        loc = min_max_func([getattr(node.location, axis) for node in sel_nodes])
        for node in sel_nodes:
            setattr(node.location, axis, loc)
        return {'FINISHED'}


class NODE_OT_node_average_distance(bpy.types.Operator):
    bl_idname = "node.average_distance"
    bl_label = "Average Node Distance"
    bl_options = {'REGISTER', 'UNDO'}

    spacing_mult = 1.2

    @property
    def _num_nodes(self):
        return len(self.nodes)

    @property
    def _avg_node_dim(self):
        real_avg = np.mean(self.dims)
        return np.mean([real_avg * 1.1, max(self.dims)])

    @property
    def _avg_node_loc(self):
        return Vector((np.mean(self.x_locs), np.mean(self.y_locs)))

    @property
    def _space_between(self):
        return self._avg_node_dim * self.spacing_mult

    def _set_start_point(self):
        total_length = (self._avg_node_dim * self.spacing_mult) * (self._num_nodes + 1)
        self.start = self._avg_node_loc.x - total_length / 2
        self.end = self._avg_node_loc.x + total_length / 2

    def _set_new_locs(self):
        mult = 1
        current_loc = self._avg_node_loc
        y_avg = self._avg_node_loc.y
        range_locs = np.arange(self.start + self._avg_node_dim, self.end, self._space_between)

        print("Range_locs: ", range_locs)
        locs = [Vector((loc, y_avg)) for loc in range_locs]
        i = 0
        for node, loc in zip(self.nodes, locs):

            node.location = loc

    @classmethod
    def poll(cls, context):
        return context.area.type == "NODE_EDITOR"

    def invoke(self, context, event):
        self.nodes = sorted(context.selected_nodes, key=lambda node: node.location.x)

        self.dims = np.array([node.dimensions.x for node in self.nodes])
        self.locs = np.array([node.location for node in self.nodes])
        self.x_locs, self.y_locs = zip(*self.locs)
        self._set_start_point()
        return self.execute(context)

    def execute(self, context):
        self._set_new_locs()
        return {'FINISHED'}


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
classes = [
    NODE_OT_directional_node_align,
    NODE_OT_node_average_distance,
]

kms = [
    {
        "keymap_operator": "node.directional_align",
        "name": "Node Editor",
        "letter": "W",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "NODE_EDITOR",
        "region_type": "WINDOW",
        "keywords": {"direction": "TOP"},
    },
    {
        "keymap_operator": "node.directional_align",
        "name": "Node Editor",
        "letter": "S",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "NODE_EDITOR",
        "region_type": "WINDOW",
        "keywords": {"direction": "BOTTOM"},
    },
    {
        "keymap_operator": "node.directional_align",
        "name": "Node Editor",
        "letter": "D",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "NODE_EDITOR",
        "region_type": "WINDOW",
        "keywords": {"direction": "RIGHT"},
    },
    {
        "keymap_operator": "node.directional_align",
        "name": "Node Editor",
        "letter": "A",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "NODE_EDITOR",
        "region_type": "WINDOW",
        "keywords": {"direction": "LEFT"},
    },
]


from my_pie_menus import utils

global addon_keymaps

addon_keymaps = []


def register():

    utils.register_classes(classes)
    utils.register_keymaps(kms, addon_keymaps)


def unregister():
    for cls in classes:
        bpy.utils.register_class(cls)
        utils.unregister_keymaps(kms)
