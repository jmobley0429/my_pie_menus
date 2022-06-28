import bpy


class NODE_OT_node_align_right(bpy.types.Operator):
    bl_idname = "node.align_right"
    bl_label = "Align nodes to right"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == "NODE_EDITOR" and bool(context.selected_nodes)

    def execute(self, context):
        sel_nodes = context.selected_nodes
        right_loc = max([node.location.x for node in sel_nodes])
        for node in sel_nodes:
            node.location.x = right_loc
        return {'FINISHED'}


class NODE_OT_node_align_left(bpy.types.Operator):
    bl_idname = "node.align_left"
    bl_label = "Align nodes to left"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == "NODE_EDITOR"

    def execute(self, context):
        sel_nodes = context.selected_nodes
        right_loc = min([node.location.x for node in sel_nodes])
        for node in sel_nodes:
            node.location.x = right_loc
        return {'FINISHED'}


class NODE_OT_node_align_top(bpy.types.Operator):
    bl_idname = "node.align_top"
    bl_label = "Align nodes to top"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == "NODE_EDITOR"

    def execute(self, context):
        sel_nodes = context.selected_nodes
        right_loc = max([node.location.y for node in sel_nodes])
        for node in sel_nodes:
            node.location.y = right_loc
        return {'FINISHED'}


class NODE_OT_node_align_bottom(bpy.types.Operator):
    bl_idname = "node.align_bottom"
    bl_label = "Align nodes to bottom"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == "NODE_EDITOR"

    def execute(self, context):
        sel_nodes = context.selected_nodes
        right_loc = min([node.location.y for node in sel_nodes])
        for node in sel_nodes:
            node.location.y = right_loc
        return {'FINISHED'}


# Register and add to the "object" menu (required to also use F3 search "Simple Object Operator" for quick access).
classes = [
    NODE_OT_node_align_right,
    NODE_OT_node_align_left,
    NODE_OT_node_align_top,
    NODE_OT_node_align_bottom,
]
