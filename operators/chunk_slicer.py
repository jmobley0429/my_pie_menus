import bpy
from mathutils import Vector


class MESH_OT_chunk_slicer(bpy.types.Operator):
    """Slice object into chunks"""

    bl_idname = "object.chunk_slicer"
    bl_label = "Chunk Slicer"

    bl_options = {'REGISTER', "UNDO"}

    cell_size: bpy.props.FloatProperty(
        name="Cell Size",
        description="Distance between each slice.",
        default=0.3,
    )
    cleanup_threshold: bpy.props.FloatProperty(
        name="Cleanup Threshold",
        description="Size of objects dimensions to delete after slice operation.",
        default=0.005,
        precision=4,
    )
    reset_origins: bpy.props.BoolProperty(
        name="Reset Origins",
        description="Set new chunk object origins to geometry center",
        default=False,
    )
    x: bpy.props.BoolProperty(
        name="X Axis",
        description="Slice on the X axis",
        default=True,
    )
    y: bpy.props.BoolProperty(
        name="Y Axis",
        description="Slice on the Y axis",
        default=True,
    )
    z: bpy.props.BoolProperty(
        name="Z Axis",
        description="Slice on the Z axis",
        default=True,
    )

    axes = list('xyz')

    @property
    def num_axes_selected(self):
        return sum([self.x, self.y, self.z])

    def _get_plane_co(self, axis):
        co = [0, 0, 0]
        index = self.axes.index(axis)
        co[index] = self.current_loc
        return co

    def _get_plane_no(self, axis):
        plane_nos = {
            'x': Vector((1, 0, 0)),
            'y': Vector((0, 1, 0)),
            'z': Vector((0, 0, 1)),
        }
        return Vector(plane_nos[axis])

    def _slices_in_axis(self, axis):
        return int(getattr(self.num_slices, axis))

    def _bmesh(cls, context):
        obj = context.obj
        mesh = obj.data
        self.bm = bmesh.new()
        self.bm.from_mesh(mesh)

    def _get_start_loc(self, axis):
        loc = min([getattr(v.co, axis) for v in self.obj.data.vertices])
        return loc

    def _get_slice_index(self, axis, index):
        return self.slice_locs[axis][index]

    def _mesh_has_manifold_geom(self):
        return all([e.is_manifold for e in self.bm.edges[:]])

    def _rename_temp(self, object):
        object.name = f"__Sliced__{self.current_index}"

    def _duplicate_obj(self, context):
        new_obj = self.obj.copy()
        new_obj.data = self.obj.data.copy()
        self._rename_temp(new_obj)
        context.collection.objects.link(new_obj)
        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = new_obj
        self.current_obj = new_obj

    def _slice(self, axis, clear_inner=False, clear_outer=False):
        self.current_obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.bisect(
            plane_co=self._get_plane_co(axis),
            plane_no=self._get_plane_no(axis),
            clear_inner=clear_inner,
            clear_outer=clear_outer,
            use_fill=True,
        )
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")

    def slice_operation_(self, context):
        self._duplicate_obj(context)
        axis = self.current_axis
        i = self.current_index
        if i != 0:
            old_loc = self.current_loc
            self.current_loc = self.slice_locs[axis][i - 1]
            self._slice(axis, clear_inner=True)
            self.current_loc = old_loc
        if i != self._slices_in_axis(axis):
            self._slice(axis, clear_outer=True)

    def _invalid_dimensions(self, dims):
        invalid = sum([v <= self.cleanup_threshold for v in dims]) > 1

        if invalid:
            print("Invalid Dims: ", dims)
            print([v < self.cleanup_threshold for v in dims])
            for d in dims:
                print(f"{d} < {self.cleanup_threshold}")
        return

    def _cleanup_objs(self, context):
        context.scene.objects.update()
        objs = context.view_layer.objects
        bpy.ops.object.select_all(action="DESELECT")
        cleanup_objs = [obj for obj in objs if "__Sliced__" in obj.name]
        orig_name = re.sub("(\.\d+$)", '', self.orig_name)
        for obj in cleanup_objs:
            dims = obj.dimensions
            if not obj.data.vertices[:] or self._invalid_dimensions(dims):
                context.collection.objects.unlink(obj)
                cleanup_objs.remove(obj)

        for i, obj in enumerate(cleanup_objs):
            if self.reset_origins:
                obj.select_set(True)
            new_name = f"{orig_name}_Sliced_{i+1}"
            obj.name = new_name
        if self.reset_origins:
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
        bpy.ops.object.select_all(action="DESELECT")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH" and context.mode == "OBJECT"

    def invoke(self, context, event):
        self.obj = context.active_object
        self.orig_name = self.obj.name
        self.mesh = self.obj.data
        self.bm = bmesh.new()
        self.bm.from_mesh(self.mesh)
        if not (self._mesh_has_manifold_geom()):
            self.report(
                {"WARNING"}, "Mesh must have manifold geometry to perform slice operation. Operation Cancelled."
            )
            return {"CANCELLED"}
        self.dims = self.obj.dimensions
        self.num_slices = Vector([dim // self.cell_size for dim in self.dims])
        self.slice_locs = defaultdict(list)
        for axis in self.axes:
            current_loc = self._get_start_loc(axis)
            for i in range(self._slices_in_axis(axis) + 1):
                new_loc = current_loc + self.cell_size
                self.slice_locs[axis].append(new_loc)
                current_loc = new_loc
        self.current_obj = self.obj
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        sliced_x = []
        sliced_y = []

        if self.num_axes_selected == 0:
            self.report({"ERROR"}, "Must select at least one slice axis.")
            return {"CANCELLED"}
        if self.x:
            self.current_axis = "x"
            x_locs = self.slice_locs[self.current_axis]
            for index, loc in enumerate(x_locs):
                self.current_loc = loc
                self.current_index = index
                self.slice_operation_(context)
                sliced_x.append(self.current_obj)
            self.obj.hide_set(True)
            self.obj.name = "Sliced_Original"
        if self.y:
            self.current_axis = "y"
            y_locs = self.slice_locs[self.current_axis]
            if not sliced_x:
                sliced_x = [self.obj]
            for obj in sliced_x:
                self.obj = obj
                for index, loc in enumerate(y_locs):
                    self.current_loc = loc
                    self.current_index = index
                    self.slice_operation_(context)
                    sliced_y.append(self.current_obj)
                context.collection.objects.unlink(obj)
        if self.z:
            self.current_axis = "z"
            z_locs = self.slice_locs[self.current_axis]
            if not sliced_y:
                if not sliced_x:
                    sliced_y = [self.obj]
                else:
                    sliced_y = sliced_x
            for obj in sliced_y:

                self.obj = obj
                for index, loc in enumerate(z_locs):
                    self.current_loc = loc
                    self.current_index = index
                    self.slice_operation_(context)
                    # sliced_y.append(self.current_obj)
                context.collection.objects.unlink(obj)

        self._cleanup_objs(context)
        return {'FINISHED'}
