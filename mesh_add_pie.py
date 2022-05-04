import bpy
from bpy.types import Menu


class PIE_MT_AddMesh(Menu):
    bl_idname = "PIE_MT_AddMesh"
    bl_label = "Pie Add Mesh"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        box = pie.split().column()
        # Left -- Cube
        op = box.operator("mesh.primitive_cube_add", text="Cube - 2m", icon="MESH_CUBE")
        op.size = 2
        op = box.operator("mesh.primitive_cube_add", text="Cube - 1m", icon="MESH_CUBE")
        op.size = 1
        op = box.operator("mesh.primitive_cube_add", text="Cube - .5m", icon="MESH_CUBE")
        op.size = 0.5

        # Right -- Cylinder
        box = pie.split().column()
        op = box.operator("mesh.primitive_cylinder_add", text="Cylinder - 32", icon="MESH_CYLINDER")
        op.vertices = 32
        op = box.operator("mesh.primitive_cylinder_add", text="Cylinder - 24", icon="MESH_CYLINDER")
        op.vertices = 16
        op = box.operator("mesh.primitive_cylinder_add", text="Cylinder - 8", icon="MESH_CYLINDER")
        op.vertices = 8

        # bottom -- Circle
        box = pie.split().column()
        op = box.operator("mesh.primitive_circle_add", text="Circle - 32", icon="MESH_CIRCLE")
        op.vertices = 32
        op = box.operator("mesh.primitive_circle_add", text="Circle - 24", icon="MESH_CIRCLE")
        op.vertices = 24
        op = box.operator("mesh.primitive_circle_add", text="Circle - 16", icon="MESH_CIRCLE")
        op.vertices = 16
        op = box.operator("mesh.primitive_circle_add", text="Circle - 8", icon="MESH_CIRCLE")
        op.vertices = 8

        # Top -- Spheres

        box = pie.split().column()
        op = box.operator("mesh.primitive_uv_sphere_add", text="UV Sphere 2m", icon="MESH_UVSPHERE")
        op.segments = 32
        op.ring_count = 16
        op.radius = 1
        op = box.operator("mesh.primitive_uv_sphere_add", text="UV Sphere 1m", icon="MESH_UVSPHERE")
        op.segments = 24
        op.ring_count = 12
        op.radius = 0.75
        op = box.operator("mesh.primitive_uv_sphere_add", text="UV Sphere .5m", icon="MESH_UVSPHERE")
        op.segments = 16
        op.ring_count = 8
        op.radius = 0.5
        op = box.operator("mesh.primitive_uv_sphere_add", text="UV Sphere - .5m", icon="MESH_UVSPHERE")
        op.segments = 12
        op.ring_count = 6
        op.radius = 0.25

        # Curves
        box = pie.split().column()

        op = box.operator("curve.primitive_bezier_curve_add", text="Bezier Curve", icon="IPO_BEZIER")

        op = box.operator("curve.primitive_nurbs_path_add", text="Path", icon="CURVE_PATH")

        op = box.operator("curve.primitive_bezier_circle_add", text="Curve Circle", icon="CURVE_NCIRCLE")

        # Planes
        box = pie.split().column()

        op = box.operator("mesh.primitive_plane_add", text="Plane", icon="MESH_PLANE")
        op = box.operator("mesh.primitive_grid_add", text="Grid", icon="MESH_GRID")
        op = box.operator("mesh.primitive_vert_add", text="Single Vert", icon="DECORATE")

        # Random
        box = pie.split().column()
        op = box.operator("mesh.primitive_torus_add", text="Torus", icon="MESH_TORUS")
        op = box.operator("mesh.primitive_ico_sphere_add", text="IcoSphere", icon="MESH_ICOSPHERE")
        op = box.operator("mesh.primitive_monkey_add", text="Monkey", icon="MESH_MONKEY")

        # empty / other
        box = pie.split().column()
        op = box.operator("object.empty_add", text="Plain Axes", icon="EMPTY_AXIS")
        op.type = "PLAIN_AXES"
        op = box.operator("object.empty_add", text="Empty Sphere", icon="SPHERE")
        op.type = "SPHERE"
        has_collections = len(bpy.data.collections) > 0
        if has_collections or len(bpy.data.collections) > 10:
            col = box
            col.operator_context = "INVOKE_REGION_WIN"
            col.operator(
                "object.collection_instance_add",
                text="Collection" if has_collections else "No Collections",
                icon="OUTLINER_OB_GROUP_INSTANCE",
            )
        else:
            col.operator_menu_enum(
                "object.collection_instance_add",
                "collection",
                text="Collection Instance",
                icon="OUTLINER_OB_GROUP_INSTANCE",
            )
