import utils
import bpy
from bpy.types import Operator
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from .custom_operator import (
    CustomOperator,
    CustomModalOperator,
    CustomBmeshOperator,
)
from ..resources import bmesh_utils as bmu


class MESH_OT_reduce_cylinder(CustomOperator, Operator):
    """Cut cylinder edges in half, select one edge ring and then execute."""

    bl_idname = "mesh.reduce_cylinder"
    bl_label = "Reduce Cylinder Edges"

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        bpy.ops.mesh.edgering_select("INVOKE_DEFAULT")
        bpy.ops.mesh.select_nth()
        bpy.ops.mesh.loop_multi_select(ring=False)
        bpy.ops.mesh.dissolve_mode(use_verts=True)
        return {'FINISHED'}


class MESH_OT_reduce_circle_segments(CustomOperator, Operator):
    """Cut cylinder edges in half, select one edge ring and then execute."""

    bl_idname = "mesh.reduce_circle_segments"
    bl_label = "Reduce Circle Segments"

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        select_vals = context.tool_settings.mesh_select_mode
        select_modes = "VERT EDGE FACE".split()
        bpy.ops.mesh.select_mode(
            use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.loop_multi_select(ring=False)
        bpy.ops.mesh.select_nth()
        bpy.ops.mesh.merge(type='COLLAPSE')
        for val, mode in zip(select_vals, select_modes):
            if val:
                bpy.ops.mesh.select_mode(
                    use_extend=True, use_expand=False, type=mode)

        return {'FINISHED'}


class MESH_OT_boundary_to_seam(CustomOperator, Operator):
    bl_idname = "mesh.boundary_to_seam"
    bl_label = "Boundary to Seam"

    def execute(self, context):
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.mark_seam()
        return {"FINISHED"}


class MESH_OT_boundary_to_sharp(CustomOperator, Operator):
    bl_idname = "mesh.boundary_to_sharp"
    bl_label = "Boundary to Sharp"

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        bpy.ops.mesh.region_to_loop()
        bpy.ops.mesh.mark_sharp()
        return {"FINISHED"}


class MESH_OT_increase_cylinder_res(CustomOperator, Operator):
    """Double Cylinder Resolution"""

    bl_idname = "mesh.increase_cylinder_res"
    bl_label = "Increase Cylinder Res"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bpy.ops.mesh.loop_multi_select(ring=True)
        bpy.ops.mesh.loop_multi_select(ring=False)
        sel_edges = [e for e in bm.edges[:] if e.select]
        bmesh.ops.subdivide_edges(bm, edges=sel_edges, cuts=1)
        bmesh.update_edit_mesh(me)
        bpy.ops.mesh.looptools_circle()
        return {'FINISHED'}


class MESH_OT_quick_tris_to_quads(CustomOperator, Operator):
    bl_idname = "mesh.quick_tris_to_quads"
    bl_label = "Quick Tris to Quads"

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        bpy.ops.mesh.quads_convert_to_tris(
            quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.mesh.tris_convert_to_quads()
        return {"FINISHED"}


def verify_weight_layer(self):
    if self.weight_type == "BEVEL":
        self.weight_layer = self.bm.edges.layers.bevel_weight.verify()
    elif self.weight_type == "CREASE":
        self.weight_layer = self.bm.edges.layers.crease.verify()


def set_edge_weight(self, edge):
    if self.clear is not None:
        val = self.clear
    else:
        val = not edge[self.weight_layer]
    edge[self.weight_layer] = float(val)


def set_edges_weight(self):
    for edge in self.sel_edges:
        try:
            set_edge_weight(self, edge)
        except ReferenceError:
            self.bmesh(context)
            set_edges_weight(self)


class MESH_OT_toggle_edge_weight(CustomBmeshOperator, Operator):

    bl_idname = "mesh.toggle_edge_weight"
    bl_label = "Set Edge Weight"
    desc_vals = [
        "Set edge weight on selected edges. Default toggle all selected edges to opposite value.",
        "CTRL - Clear all edges.",
        "ALT - Set all edges weight to 1",
    ]
    bl_description = '\n'.join(desc_vals)
    bl_options = {'REGISTER', 'UNDO'}

    weight_type: bpy.props.StringProperty(name='Weight Type')
    clear = None

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def invoke(self, context, event):
        if event.alt:
            self.clear = True
        elif event.ctrl:
            self.clear = False
        self.bmesh(context)
        return self.execute(context)

    def execute(self, context):
        verify_weight_layer(self)
        set_edges_weight(self)
        bmesh.update_edit_mesh(context.edit_object.data)
        return {"FINISHED"}


class MESH_OT_set_sharp_to_weighted(CustomBmeshOperator, Operator):
    bl_idname = "mesh.set_sharp_to_weighted"
    bl_label = "Sharp To Weighted"
    bl_options = {'REGISTER', 'UNDO'}

    weight_type: bpy.props.StringProperty(name="Weight Type", default="BEVEL")
    sharpness: bpy.props.IntProperty(name="Sharpness", default=30)

    @property
    def sharp_angle(self):
        return np.radians(self.sharpness)

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def invoke(self, context, event):
        self.bmesh(context)
        return self.execute(context)

    def execute(self, context):
        obj = self.get_active_obj()
        stored_edges = [e for e in self.sel_edges]
        self.select_edges(context, self.bm.edges[:], select=False)
        self.select_sharp_edges(threshold=self.sharp_angle)
        verify_weight_layer(self)
        set_edges_weight(self)
        if stored_edges:
            self.select_edges(context, self.bm.edges[:], select=False)
            self.select_edges(context, stored_edges, select=True)
        bmesh.update_edit_mesh(context.edit_object.data)
        return {"FINISHED"}


class MESH_OT_set_boundary_to_weighted(CustomBmeshOperator, Operator):
    bl_idname = "mesh.set_boundary_to_weighted"
    bl_label = "Boundary To Weighted"
    bl_options = {'REGISTER', 'UNDO'}

    weight_type: bpy.props.StringProperty(name="Weight Type", default="BEVEL")

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def invoke(self, context, event):
        self.bmesh(context)
        return self.execute(context)

    def execute(self, context):
        obj = self.get_active_obj()
        stored_edges = [e for e in self.sel_edges]
        self.select_edges(
            context, self.bm.edges[:], select=False, skip_callback_func=self.is_boundary_edge)
        verify_weight_layer(self)
        set_edges_weight(self)
        self.bmesh(context)
        if stored_edges:
            self.select_edges(context, self.bm.edges[:], select=False)
            self.select_edges(context, stored_edges, select=True)
        bmesh.update_edit_mesh(context.edit_object.data)
        return {"FINISHED"}


class MESH_OT_weld_verts_to_active(Operator):

    '''Weld all selected verts to active vertex.'''

    bl_idname = "mesh.weld_verts_to_active"
    bl_label = "Weld to Active"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH" and "EDIT" in context.mode

    def get_bmesh(self, context):
        self.obj = context.edit_object
        self.mesh = self.obj.data
        self.bm = bmesh.from_edit_mesh(self.mesh)

    def execute(self, context):
        try:
            bpy.ops.view3d.snap_selected_to_active()
            bpy.ops.mesh.remove_doubles(use_unselected=True)
        except RuntimeError:
            bpy.ops.mesh.merge(type="CENTER")
        return {"FINISHED"}


class ToggleAnnotateProps(bpy.types.PropertyGroup):
    scene_prop_id = "ToggleAnnotateProps"
    bl_idname = "ToggleAnnotateProps"
    prev_tool: bpy.props.StringProperty()


class VIEW3D_OT_toggle_annotate(Operator):
    bl_idname = "view3d.toggle_annotate"
    bl_label = "Toggle Annotate"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        self.mode = context.mode
        self.props = context.window_manager.ToggleAnnotateProps
        self.prev_tool = self.props.prev_tool
        return self.execute(context)

    def execute(self, context):
        tools = context.workspace.tools
        curr_tool = tools.from_space_view3d_mode(
            self.mode, create=False).idname
        if self.prev_tool is None or curr_tool != "builtin.annotate":
            bpy.ops.wm.tool_set_by_id(name="builtin.annotate")
        else:
            bpy.ops.wm.tool_set_by_id(name=self.prev_tool)
        context.window_manager.ToggleAnnotateProps.prev_tool = curr_tool
        return {"FINISHED"}


class MESH_OT_poke_hole_in_faces(CustomBmeshOperator, CustomModalOperator, Operator):
    bl_idname = "mesh.poke_hole_in_faces"
    bl_label = "Poke Hole in Face"
    bl_options = {'REGISTER', 'UNDO'}

    offset_multiplier: bpy.props.FloatProperty(
        name="Offset Multiplier", default=0.2)
    bridge = False

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def poke_hole(self):
        ret = bmesh.ops.poke(self.bm, faces=self.sel_faces)
        center = ret['verts'][:]
        self.select_elem_in_list(self.bm.verts[:], center)
        del ret
        for face in self.bm.faces[:]:
            face.select_set(False)
        self.bm.select_flush_mode()
        ret = bmesh.ops.bevel(self.bm, geom=center,
                              offset=self.offset_amt, segments=2)
        verts = ret['verts']
        faces = ret['faces']
        del ret
        bmesh.ops.delete(self.bm, geom=faces, context="FACES")
        self.select_elem_in_list(self.bm.verts[:], verts)
        bmesh.update_edit_mesh(self.mesh)
        bpy.ops.mesh.select_mode(
            use_extend=False, use_expand=False, type='VERT')
        bpy.ops.mesh.looptools_circle()

    def invoke(self, context, event):
        self.bmesh(context)
        self.sel_faces = [f for f in self.bm.faces[:] if f.select]
        self.offset_amt = np.mean(
            [f.calc_area() for f in self.sel_faces]) * self.offset_multiplier
        # self.init_mouse_x = event.mouse_x
        if event.alt:
            self.bridge = True
        return self.execute(context)

    def execute(self, context):
        self.poke_hole()
        if self.bridge:
            bpy.ops.mesh.bridge_edge_loops()
        return {"FINISHED"}


class MESH_OT_origin_to_bottom_left(Operator):
    bl_idname = "mesh.origin_to_bottom_left"
    bl_label = "Origin to Bottom Left"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = bpy.context.object
        mesh = obj.data
        bb = obj.bound_box
        bb_locs = np.array([v[:] for v in bb])
        bot_left = Vector([min(row) for row in bb_locs.transpose()])
        mat = Matrix.Translation(-bot_left)
        if mesh.is_editmode:
            bm = bmesh.from_edit_mesh(mesh)
            bm.transform(mat)
            bmesh.update_edit_mesh(me, False, False)
        else:
            mesh.transform(mat)
        mesh.update()
        obj.matrix_world.translation = bot_left
        return {"FINISHED"}


class MESH_OT_smart_join_verts(CustomBmeshOperator, Operator):
    bl_idname = "mesh.smart_join_verts"
    bl_label = "Smart Join Verts"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        self.bmesh(context)
        sel_verts = set([v for v in self.bm.verts[:] if v.select])
        active_vert = set([self.bm.select_history.active])
        one_edge = len(sel_verts) == 2
        non_active = sel_verts - active_vert
        if not active_vert and not one_edge:
            self.report({"ERROR"}, "At least one vert must be active.")
            return {"CANCELLED"}
        if one_edge:
            bmesh.ops.connect_vert_pair(self.bm, verts=list(sel_verts))
        else:
            active = list(active_vert)[0]
            for vert in non_active:
                pair = [vert, active]
                bmesh.ops.connect_vert_pair(self.bm, verts=pair)
        bmesh.update_edit_mesh(self.mesh)
        return {"FINISHED"}


def toggle_retopo_visibility(context):
    sd = context.space_data
    obj = context.object
    hidden_wire = sd.show_occlude_wire
    in_front = obj.show_in_front
    wire = obj.show_wire
    overlays = [hidden_wire, in_front, wire]

    toggled = all(overlays)
    for ol in overlays:
        ol = toggled


class MESH_toggle_retopo_visibility(Operator):
    bl_idname = "mesh.toggle_retopo_visibility"
    bl_label = "Toggle Retopo View"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        toggle_retopo_visibility(context)
        return {"FINISHED"}


def get_bm(context):
    obj = context.edit_object
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    return bm


def has_sel_faces(context):
    bm = get_bm(context)
    sel_faces = bool(get_selected(bm, "faces"))
    bm.free()
    del bm
    return sel_faces


def get_selected(mesh, elem_type):
    return [elem for elem in getattr(mesh, elem_type)[:] if elem.select]


def get_face_edges(bm, face):
    edges = [edge.index for edge in face.edges[:]]
    ret = [edge for edge in bm.edges[:] if edge.index in edges]
    return ret


def dissolve_faces(bm, faces):

    return ret["faces"]


def smart_grid_fill(context, args):
    span = args.pop('span')
    offset = args.pop('offset')
    obj = context.edit_object
    bm = get_bm(context)
    sel_faces = get_selected(bm, "faces")
    if sel_faces:
        if len(sel_faces) > 1:
            ret = bmesh.ops.dissolve_faces(bm, faces=sel_faces)
            face = ret["region"][0]
        else:
            face = sel_faces[0]
        face_edges = get_face_edges(bm, face)
        bm.faces.remove(face)
        for edge in face_edges[:]:
            edge.select_set(True)
        bm.select_flush(True)
        bmesh.update_edit_mesh(obj.data)
    bpy.ops.mesh.fill_grid("INVOKE_DEFAULT", span=span, offset=offset)


class MESH_OT_smart_grid_fill(Operator):
    bl_idname = "mesh.smart_grid_fill"
    bl_label = "Grid Fill"
    bl_options = {'REGISTER', 'UNDO'}

    span: bpy.props.IntProperty(default=1, name="Span")
    offset: bpy.props.IntProperty(default=0, name="Offset")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and "EDIT" in context.mode

    def execute(self, context):
        args = self.as_keywords()
        smart_grid_fill(context, args)
        return {"FINISHED"}


def toggle_retopo_overlays(context):
    obj = context.object
    overlay_attrs = ["show_in_front", "show_wire", "show_all_edges"]
    overlay_vals = [getattr(obj, attr) for attr in overlay_attrs]
    is_retopo_view = any(overlay_vals)
    toggle_val = not is_retopo_view
    for attr in overlay_attrs:
        setattr(obj, attr, toggle_val)
    context.space_data.shading.light = 'MATCAP'
    context.space_data.shading.color_type = 'OBJECT'
    if toggle_val:
        obj.color = [0.000000, 0.650000, 1.000000, 0.500000]
    else:
        obj.color = [1.000000, 1.000000, 1.000000, 1.000000]


class MESH_OT_toggle_retopo_overlays(Operator):
    bl_idname = "mesh.toggle_retopo_overlays"
    bl_label = "Toggle Retopo Views"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        toggle_retopo_overlays(context)
        return {"FINISHED"}


def origin_to_bot_left_menu_func(self, context):
    layout = self.layout
    pie = layout.menu_pie()
    op = pie.operator('mesh.origin_to_bottom_left')


class CleanupMesh:

    def __init__(self, context, args, op=None):
        if op is not None:
            self.op = op
        self._set_args(args)
        self.context = context
        self.obj = context.edit_object
        self.mesh = self.obj.data
        self.bm = bmesh.from_edit_mesh(self.mesh)
        
    @property
    def _select_state_from_mode(self):
        modes = "VERT EDGE FACE".split()
        bm_modes=  []
        for mode in modes:
            if mode in self.bm.select_mode:
                bm_modes.append(True)
            else:
                bm_modes.append(False)
        return tuple(bm_modes)


    def _set_args(self, args):
        if args:
            for key, value in args.items():
                setattr(self, key, value)

    def _finish_op(self):
        self.context.tool_settings.mesh_select_mode = self._select_state_from_mode
        self.bm.select_flush_mode()
        bmesh.update_edit_mesh(self.mesh)

    def select_short_edges(self, ):
        self.selected = 0
        for e in self.bm.edges[:]:
            e.select_set(False)
            length = e.calc_length()
            if length < self.edge_threshold:
                e.select_set(True)
                self.selected += 1
        self.bm.select_mode = {"EDGE"}
        self._finish_op()
        if not self.selected:
            self.op.report({"INFO"}, "No short edges found!")
        return {"FINISHED"}
        
    def select_small_faces(self, ):
        self.selected = 0
        for face in self.bm.faces[:]:
            face.select_set(False)
            area = face.calc_area()
            if area < self.face_threshold:
                face.select_set(True)
                self.selected += 1
        self.bm.select_mode = {"FACE"}
        self._finish_op()
        if not self.selected:
            self.op.report({"INFO"}, "No small faces found!")
        return {"FINISHED"}

    def select_ngons(self):
        self.selected = 0
        for face in self.bm.faces:
            if len(face.edges[:]) > 4:
                face.select_set(True)
                self.selected += 1
            else:
                face.select_set(False)
        self.bm.select_mode = {"FACE"}
        self._finish_op() 
        if not self.selected:
            self.op.report({"INFO"}, "No ngons found!")
        return {"FINISHED"}
            

    def cleanup_ngons(self):
        self.select_ngons()
        if self.selected:
            bpy.ops.mesh.quick_tris_to_quads()
            bpy.ops.mesh.select_all(action="DESELECT")
        return {"FINISHED"}

class MESH_OT_cleanup_select_ngons(CustomOperator, bpy.types.Operator):
    bl_idname = "mesh.cleanup_select_ngons"
    bl_label = "Select Ngons"
    bl_options = {"REGISTER", "UNDO"}

    ngon_side_count: bpy.props.IntProperty(name='Ng     return {"FINISHED"}on Side Count', default=5)

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def invoke(self, context, event):
        self.args = self.as_keywords()
        return self.execute(context)


    def execute(self, context):
        cleaner = CleanupMesh(context, self.args, op=self)
        return cleaner.select_ngons()


class MESH_OT_cleanup_select_small_faces(CustomOperator, bpy.types.Operator):
    bl_idname = "mesh.cleanup_select_small_faces"
    bl_label = "Select Small Faces"

    face_threshold: bpy.props.FloatProperty(
        name='Face Threshold', default=.0001)

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def invoke(self, context, event):
        self.args = self.as_keywords()
        return self.execute(context)

    def execute(self, context):
        cleaner = CleanupMesh(context, self.args, op=self)
        return cleaner.select_small_faces()
        


class MESH_OT_cleanup_select_short_edges(CustomOperator, bpy.types.Operator):
    bl_idname = "mesh.cleanup_select_short_edges"
    bl_label = "Select Short Edges"

    edge_threshold: bpy.props.FloatProperty(
        name='Edge Threshold', default=.001)

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def invoke(self, context, event):
        self.args = self.as_keywords()
        return self.execute(context)

    def execute(self, context):
        cleaner = CleanupMesh(context, self.args, op=self)
        return cleaner.select_short_edges()
        


class MESH_OT_cleanup_handle_ngons(CustomOperator, bpy.types.Operator):
    bl_idname = "mesh.cleanup_handle_ngons"
    bl_label = "Cleanup Ngons"

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def invoke(self, context, event):
        self.args = self.as_keywords()
        return self.execute(context)

    def execute(self, context):
        cleaner = CleanupMesh(context, self.args, op=self)
        return cleaner.cleanup_ngons()
        


def subdivide_inner_edges(context):
    obj = context.edit_object
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    sel_edges = bmu.get_sel_edges(bm)
    subdiv_edges = []

    for edge in sel_edges:
        edge.select_set(False)
        if bmu.is_interior(edge) or edge.is_boundary:
            subdiv_edges.append(edge)

    ret = bmesh.ops.subdivide_edges(bm, edges=subdiv_edges, cuts=1)
    for geo in ret['geom_inner']:
        if isinstance(geo, bmesh.types.BMEdge):
            geo.select_set(True)
    bm.select_flush(True)
    bmesh.update_edit_mesh(mesh)
    bm.free()
    del bm


class MESH_OT_subdivide_inner_edges(CustomOperator, bpy.types.Operator):
    bl_idname = "mesh.subdivide_inner_edges"
    bl_label = "Subdivide Inner Edges"

    @classmethod
    def poll(cls, context):
        return cls.edit_obj_poll(context)

    def execute(self, context):
        subdivide_inner_edges(context)
        return {"FINISHED"}


classes = (
    MESH_OT_reduce_cylinder,
    MESH_OT_reduce_circle_segments,
    MESH_OT_increase_cylinder_res,
    MESH_OT_boundary_to_sharp,
    MESH_OT_boundary_to_seam,
    MESH_OT_quick_tris_to_quads,
    MESH_OT_toggle_edge_weight,
    MESH_OT_set_sharp_to_weighted,
    MESH_OT_set_boundary_to_weighted,
    MESH_OT_weld_verts_to_active,
    VIEW3D_OT_toggle_annotate,
    MESH_OT_poke_hole_in_faces,
    MESH_OT_origin_to_bottom_left,
    ToggleAnnotateProps,
    MESH_OT_smart_join_verts,
    MESH_toggle_retopo_visibility,
    MESH_OT_smart_grid_fill,
    MESH_OT_toggle_retopo_overlays,
    MESH_OT_cleanup_select_short_edges,
    MESH_OT_cleanup_select_small_faces,
    MESH_OT_cleanup_select_ngons,
    MESH_OT_cleanup_handle_ngons,
    MESH_OT_subdivide_inner_edges,
)

kms = [
    {
        "keymap_operator": "mesh.reduce_cylinder",
        "name": "Mesh",
        "letter": "X",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {},
    },
    {
        "keymap_operator": "view3d.toggle_annotate",
        "name": "Object Mode",
        "letter": "D",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {},
    },
]


kms = []

addon_keymaps = []


def register():
    utils.register_classes(classes)
    utils.register_keymaps(kms, addon_keymaps)
    bpy.types.WindowManager.ToggleAnnotateProps = bpy.props.PointerProperty(
        type=ToggleAnnotateProps)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        utils.unregister_keymaps(kms)
    del bpy.types.WindowManager.ToggleAnnotateProps


