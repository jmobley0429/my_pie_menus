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
        op = box.operator("mesh.primitive_cube_add", text="Cube - 1m", icon="MESH_CUBE")
        op.size = 1
        op = box.operator("mesh.primitive_cube_add", text="Cube - .5m", icon="MESH_CUBE")
        op.size = 0.5
        op = box.operator("mesh.primitive_cube_add", text="Cube - .25m", icon="MESH_CUBE")
        op.size = 0.25

        # Right -- Cylinder
        box = pie.split().column()
        op = box.operator("mesh.primitive_uv_sphere_add", text="UV Sphere", icon="MESH_UVSPHERE")
        op.segments = 32
        op.ring_count = 16
        op.radius = 1
        op = box.operator("mesh.primitive_ico_sphere_add", text="IcoSphere", icon="MESH_ICOSPHERE")
        op = box.operator("mesh.primitive_round_cube_add", text="QuadSphere", icon="MESH_UVSPHERE")
        op.arc_div = 8
        op.radius = 1
        op.div_type = "CORNERS"

        # bottom -- Circle
        box = pie.split().column()
        box.label(text="Circle")
        spl = box.split()
        op = spl.operator("mesh.primitive_circle_add", text="6", icon="MESH_CIRCLE")
        op.vertices = 6
        op = spl.operator("mesh.primitive_circle_add", text="12", icon="MESH_CIRCLE")
        op.vertices = 12
        spl = box.split()
        op = spl.operator("mesh.primitive_circle_add", text="8", icon="MESH_CIRCLE")
        op.vertices = 8
        op = spl.operator("mesh.primitive_circle_add", text="16", icon="MESH_CIRCLE")
        op.vertices = 16
        spl = box.split()
        op = spl.operator("mesh.primitive_circle_add", text="24", icon="MESH_CIRCLE")
        op.vertices = 24
        op = spl.operator("mesh.primitive_circle_add", text="48", icon="MESH_CIRCLE")
        op.vertices = 48
        spl = box.split()
        op = spl.operator("mesh.primitive_circle_add", text="32", icon="MESH_CIRCLE")
        op.vertices = 32
        op = spl.operator("mesh.primitive_circle_add", text="64", icon="MESH_CIRCLE")
        op.vertices = 64

        # Top -- Spheres
        box = pie.split().column()
        box.label(text="Cylinder")
        spl = box.split()
        op = spl.operator("mesh.primitive_cylinder_add", text="6", icon="MESH_CYLINDER")
        op.vertices = 6
        op = spl.operator("mesh.primitive_cylinder_add", text="12", icon="MESH_CYLINDER")
        op.vertices = 12
        spl = box.split()
        op = spl.operator("mesh.primitive_cylinder_add", text="8", icon="MESH_CYLINDER")
        op.vertices = 8
        op = spl.operator("mesh.primitive_cylinder_add", text="16", icon="MESH_CYLINDER")
        op.vertices = 16
        spl = box.split()
        op = spl.operator("mesh.primitive_cylinder_add", text="24", icon="MESH_CYLINDER")
        op.vertices = 24
        op = spl.operator("mesh.primitive_cylinder_add", text="48", icon="MESH_CYLINDER")
        op.vertices = 48
        spl = box.split()
        op = spl.operator("mesh.primitive_cylinder_add", text="32", icon="MESH_CYLINDER")
        op.vertices = 32
        op = spl.operator("mesh.primitive_cylinder_add", text="64", icon="MESH_CYLINDER")
        op.vertices = 64

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
        op = box.operator("mesh.primitive_cone_add", text="Cone", icon="MESH_CONE")
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


class PIE_MT_ParticleSubPie(Menu):
    bl_idname = "PIE_MT_ParticleSubPie"
    bl_label = "Pie Add Particle Modifiers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type != 'GPENCIL'

    def draw(self, context):
        layout = self.layout
        op = layout.operator("object.modifier_add", text="Cloth", icon="MOD_CLOTH")
        op.type = "CLOTH"
        op = layout.operator("object.modifier_add", text="Particle", icon="PARTICLES")
        op.type = "PARTICLE_SYSTEM"
        op = layout.operator("object.modifier_add", text="Soft Body", icon="MOD_SOFT")
        op.type = "SOFT_BODY"
        op = layout.operator("rigidbody.object_add", text="Rigid Body", icon="RIGID_BODY")


class PIE_MT_MeshSubPie(Menu):
    bl_idname = "PIE_MT_MeshSubPie"
    bl_label = "Pie Add Mesh Modifiers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type != 'GPENCIL'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.custom_remesh", text="Remesh", icon="MOD_REMESH")
        layout.operator("object.custom_decimate", text="Decimate", icon="MOD_DECIM")
        op = layout.operator("object.modifier_add", text="Smooth", icon="MOD_SMOOTH")
        op.type = "SMOOTH"
        op = layout.operator("object.modifier_add", text="Wireframe", icon="MOD_WIREFRAME")
        op.type = "WIREFRAME"


class PIE_MT_NormalSubPie(Menu):
    bl_idname = "PIE_MT_NormalSubPie"
    bl_label = "Pie Add Normal Modifiers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type != 'GPENCIL'

    def draw(self, context):
        layout = self.layout
        op = layout.operator("object.modifier_add", text="Weighted Normal", icon="NORMALS_VERTEX")
        op.type = "WEIGHTED_NORMAL"
        op = layout.operator("object.modifier_add", text="UV Project", icon="MOD_UVPROJECT")
        op.type = "UV_PROJECT"
        op = layout.operator("object.modifier_add", text="Data Transfer", icon="CON_TRANSLIKE")
        op.type = "DATA_TRANSFER"


class PIE_MT_AddModifier(Menu):
    bl_idname = "PIE_MT_AddModifier"
    bl_label = "Pie Add Modifier"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type != 'GPENCIL'

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Left -- Mirror
        pie = layout.menu_pie()
        box = pie.split().column()
        box.label(text="Mirror")
        box.scale_x = 1.2
        spl = box.split()
        op = spl.operator('object.custom_mirror_modifier', text="X -", icon="MOD_MIRROR")
        op.mirror_type = "X_POS"
        op = spl.operator('object.custom_mirror_modifier', text="X +", icon="MOD_MIRROR")
        op.mirror_type = "X_NEG"
        spl = box.split()
        op = spl.operator('object.custom_mirror_modifier', text="Y -", icon="MOD_MIRROR")
        op.mirror_type = "Y_POS"
        op = spl.operator('object.custom_mirror_modifier', text="Y +", icon="MOD_MIRROR")
        op.mirror_type = "Y_NEG"
        spl = box.split()
        op = spl.operator('object.custom_mirror_modifier', text="Z -", icon="MOD_MIRROR")
        op.mirror_type = "Z_POS"
        op = spl.operator('object.custom_mirror_modifier', text="Z +", icon="MOD_MIRROR")
        op.mirror_type = "Z_NEG"
        # Right -- Bevel / Shading
        box = pie.split().column()
        box.operator('object.custom_bevel_modifier', text="Bevel", icon="MOD_BEVEL")
        box.operator('object.custom_bevel_subsurf_modifier', text="Bevel Subsurf", icon="MOD_SUBSURF")
        op = box.operator('object.modifier_add', text="Weighted Normal", icon="MOD_NORMALEDIT")
        op.type = "WEIGHTED_NORMAL"
        # Bottom -- Deform
        box = pie.split().column()
        box.operator("object.custom_simple_deform", text="Bend", icon="MOD_SIMPLEDEFORM")
        box.operator("object.custom_displace", text="Displace", icon="MOD_DISPLACE")
        box.operator("object.custom_shrinkwrap", text="Shrinkwrap", icon="MOD_SHRINKWRAP")
        box.operator("object.custom_lattice", text="Lattice", icon="OUTLINER_DATA_LATTICE")
        # Top -- Mesh \ Edges
        box = pie.split().column()
        op = box.operator("object.array_modal", text="Array", icon="MOD_ARRAY")
        box.operator("object.solidify_modal", text="Solidify", icon="MOD_SOLIDIFY")
        box.operator("object.screw_modal", text="Screw", icon="MOD_SCREW")
        # TL --
        op = pie.menu('PIE_MT_ParticleSubPie', text="Physics", icon='PHYSICS')
        # TR --
        op = pie.menu("PIE_MT_MeshSubPie", text="Mesh", icon='MOD_REMESH')
        # BL --
        op = pie.operator("object.modifier_add", text="Geometry Nodes", icon="NODETREE")
        op.type = "NODES"
        # BL --
        op = pie.menu("PIE_MT_NormalSubPie", text="Normals and UVs", icon="SNAP_NORMAL")


class PIE_MT_AddOtherObjects(Menu):
    bl_idname = "PIE_MT_AddOtherObjects"
    bl_label = "Pie Add Other Objects"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # Left -- Lights
        pie.operator_menu_enum("object.light_add", "type")
        # Right -- Camera
        pie.operator("object.smart_add_camera", text="Add Camera", icon="CAMERA_DATA")
        # Bottom -- Light Probe
        pie.operator_menu_enum("object.lightprobe_add", "type")
        # Top -- Smart Lattice
        pie.operator("import_image.to_plane", text="Image as Plane", icon="FILE_IMAGE")
        # Text
        pie.operator("object.text_add", text="Text", icon="SMALL_CAPS")
        # Mannequin
        pie.operator("mesh.primitive_mannequin_add", text="Mannequin", icon="OUTLINER_OB_ARMATURE")
        # Armature
        pie.operator("object.armature_add", text="Armature", icon="ARMATURE_DATA")
        # Metaball
        pie.operator_menu_enum("object.metaball_add", "type")


classes = (
    PIE_MT_AddMesh,
    PIE_MT_ParticleSubPie,
    PIE_MT_MeshSubPie,
    PIE_MT_NormalSubPie,
    PIE_MT_AddModifier,
    PIE_MT_AddOtherObjects,
)
