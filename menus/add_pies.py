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
        spl = box.split()
        op = spl.operator("mesh.custom_cube_add", text="1m", icon="MESH_CUBE")
        op.size = 1
        op = spl.operator("mesh.custom_cube_add", text="10m", icon="MESH_CUBE")
        op.size = 10
        spl = box.split()
        op = spl.operator("mesh.custom_cube_add", text=".5m", icon="MESH_CUBE")
        op.size = 0.5
        op = spl.operator("mesh.custom_cube_add", text="5m", icon="MESH_CUBE")
        op.size = 5
        spl = box.split()
        op = spl.operator("mesh.custom_cube_add", text=".25m", icon="MESH_CUBE")
        op.size = 0.25
        op = spl.operator("mesh.custom_cube_add", text="2m", icon="MESH_CUBE")
        op.size = 2

        # Right -- Sphere
        col = pie.column()
        spl = col.split()
        op = spl.operator("mesh.primitive_uv_sphere_add", text="UV - 32", icon="MESH_UVSPHERE")
        op.segments = 32
        op.ring_count = 16
        op.radius = 1
        op = spl.operator("mesh.primitive_uv_sphere_add", text="UV - 16", icon="MESH_UVSPHERE")
        op.segments = 16
        op.ring_count = 8
        op.radius = 1
        spl = col.split()
        op = spl.operator("mesh.primitive_ico_sphere_add", text="Ico - 2", icon="MESH_ICOSPHERE")
        op.subdivisions = 2
        op = spl.operator("mesh.primitive_ico_sphere_add", text="Ico - 1", icon="MESH_ICOSPHERE")
        op.subdivisions = 2
        spl = col.split()
        op = spl.operator("mesh.primitive_round_cube_add", text="Quad - 8", icon="MESH_UVSPHERE")
        op.arc_div = 8
        op.radius = 1
        op.div_type = "CORNERS"
        op = spl.operator("mesh.primitive_round_cube_add", text="Quad - 4", icon="MESH_UVSPHERE")
        op.arc_div = 4
        op.radius = 1
        op.div_type = "CORNERS"

        # bottom -- Circle
        box = pie.split().column()
        spl = box.split()
        op = spl.operator("mesh.primitive_circle_add", text="6", icon="MESH_CIRCLE")
        op.vertices = 6
        op.radius = 0.125
        op = spl.operator("mesh.primitive_circle_add", text="12", icon="MESH_CIRCLE")
        op.vertices = 12
        op.radius = 0.125
        spl = box.split()
        op = spl.operator("mesh.primitive_circle_add", text="8", icon="MESH_CIRCLE")
        op.vertices = 8
        op.radius = 0.125
        op = spl.operator("mesh.primitive_circle_add", text="16", icon="MESH_CIRCLE")
        op.vertices = 16
        op.radius = 0.125
        spl = box.split()
        op = spl.operator("mesh.primitive_circle_add", text="24", icon="MESH_CIRCLE")
        op.vertices = 24
        op.radius = 0.125
        op = spl.operator("mesh.primitive_circle_add", text="48", icon="MESH_CIRCLE")
        op.vertices = 48
        op.radius = 0.125
        spl = box.split()
        op = spl.operator("mesh.primitive_circle_add", text="32", icon="MESH_CIRCLE")
        op.vertices = 32
        op.radius = 0.125
        op = spl.operator("mesh.primitive_circle_add", text="64", icon="MESH_CIRCLE")
        op.vertices = 64
        op.radius = 0.125

        # Top -- Cylinder
        box = pie.split().column()
        box.ui_units_y -= 25
        spl = box.split()
        op = spl.operator("mesh.custom_cylinder_add", text="6", icon="MESH_CYLINDER")
        op.vertices = 6
        op = spl.operator("mesh.custom_cylinder_add", text="12", icon="MESH_CYLINDER")
        op.vertices = 12
        spl = box.split()
        op = spl.operator("mesh.custom_cylinder_add", text="8", icon="MESH_CYLINDER")
        op.vertices = 8
        op = spl.operator("mesh.custom_cylinder_add", text="16", icon="MESH_CYLINDER")
        op.vertices = 16
        spl = box.split()
        op = spl.operator("mesh.custom_cylinder_add", text="24", icon="MESH_CYLINDER")
        op.vertices = 24
        op = spl.operator("mesh.custom_cylinder_add", text="48", icon="MESH_CYLINDER")
        op.vertices = 48
        spl = box.split()
        op = spl.operator("mesh.custom_cylinder_add", text="32", icon="MESH_CYLINDER")
        op.vertices = 32
        op = spl.operator("mesh.custom_cylinder_add", text="64", icon="MESH_CYLINDER")
        op.vertices = 64

        box = pie.split().column()
        spl = box.split()
        op = spl.operator("mesh.primitive_plane_add", text="Plane 1m", icon="MESH_PLANE")
        op.size = 1
        op = spl.operator("mesh.primitive_plane_add", text="Plane .5m", icon="MESH_PLANE")
        op.size = 0.5
        spl = box.split()
        op = spl.operator("mesh.primitive_grid_add", text="Grid 25", icon="MESH_GRID")
        op.x_subdivisions = 25
        op.y_subdivisions = 25
        op = spl.operator("mesh.primitive_grid_add", text="Grid 10", icon="MESH_GRID")
        spl = box.split()
        op = spl.operator("mesh.primitive_round_cube_add", text="3D Grid", icon="GRID")
        op.radius = 0.0
        op.lin_div = 5
        op.div_type = "ALL"
        op = spl.operator("mesh.primitive_vert_add", text="Single Vert", icon="DECORATE")

        # Planes
        # empty / other
        box = pie.split().column()
        box.ui_units_y -= 5
        box.ui_units_x -= 5
        spl = box.split()
        op = spl.operator("object.empty_add", text="Plain Axes", icon="EMPTY_AXIS")
        op.type = "PLAIN_AXES"
        op = spl.operator("object.empty_add", text="Arrows", icon="EMPTY_ARROWS")
        op.type = "ARROWS"
        spl = box.split()
        op = spl.operator("object.empty_add", text="Cube", icon="CUBE")
        op.type = "CUBE"
        op = spl.operator("object.empty_add", text="Circle", icon="MESH_CIRCLE")
        op.type = "CIRCLE"
        spl = box.split()
        op = spl.operator("object.empty_add", text="Sphere", icon="CUBE")
        op.type = "SPHERE"
        has_collections = len(bpy.data.collections) > 0
        if has_collections or len(bpy.data.collections) > 10:
            col = box
            spl.operator_context = "INVOKE_REGION_WIN"
            spl.operator(
                "object.collection_instance_add",
                text="Collection" if has_collections else "No Collections",
                icon="OUTLINER_OB_GROUP_INSTANCE",
            )
        else:
            spl.operator_menu_enum(
                "object.collection_instance_add",
                "collection",
                text="Collection Instance",
                icon="OUTLINER_OB_GROUP_INSTANCE",
            )

        # Random
        box = pie.split().column()
        box.ui_units_y += 2
        op = box.operator("mesh.primitive_torus_add", text="Torus", icon="MESH_TORUS")
        op = box.operator("mesh.primitive_cone_add", text="Cone", icon="MESH_CONE")
        op = box.operator("mesh.primitive_monkey_add", text="Monkey", icon="MESH_MONKEY")

        # Curves
        box = pie.split().column()
        box.ui_units_y += 2
        op = box.operator("curve.primitive_bezier_curve_add", text="Bezier Curve", icon="IPO_BEZIER")
        op = box.operator("curve.primitive_nurbs_path_add", text="Path", icon="CURVE_PATH")
        op = box.operator("curve.primitive_bezier_circle_add", text="Curve Circle", icon="CURVE_NCIRCLE")


class PIE_MT_PhysicsSubPie(Menu):
    bl_idname = "PIE_MT_PhysicsSubPie"
    bl_label = "Pie Add Physics Modifiers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type != 'GPENCIL'

    def draw(self, context):
        layout = self.layout
        op = layout.operator("object.modifier_add", text="Cloth", icon="MOD_CLOTH")
        op.type = "CLOTH"
        op = layout.operator("object.modifier_add", text="Collision", icon="MOD_PHYSICS")
        op.type = "COLLISION"
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
        op = layout.operator("object.modifier_add", text="Multires", icon="MOD_MULTIRES")
        op.type = "MULTIRES"
        layout.operator("object.custom_remesh", text="Remesh", icon="MOD_REMESH")
        layout.operator("object.custom_decimate", text="Decimate", icon="MOD_DECIM")
        op = layout.operator("object.modifier_add", text="Smooth", icon="MOD_SMOOTH")
        op.type = "SMOOTH"
        op = layout.operator("object.modifier_add", text="Wireframe", icon="MOD_WIREFRAME")
        op.type = "WIREFRAME"


class PIE_MT_add_armature_extended(Menu):
    bl_idname = "PIE_MT_add_armature_extended"
    bl_label = "Pie Add Armature Extended"
    bl_options = {"REGISTER", "UNDO"}

    def draw(self, context):
        layout = self.layout
        layout.operator("object.armature_add", text="Single Bone", icon="BONE_DATA")
        layout.menu('ARMATURE_MT_Basic_class')
        layout.menu('ARMATURE_MT_Animals_class')


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
        obj = context.active_object
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
        if obj.type == "MESH":
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
        op = pie.menu('PIE_MT_PhysicsSubPie', text="Physics", icon='PHYSICS')
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
        box = pie.split().column()
        box.label(text="Light")
        spl = box.split()
        op = spl.operator("object.light_add", text="Point", icon="LIGHT_POINT")
        op.type = "POINT"
        op = spl.operator("object.light_add", text="Area", icon="LIGHT_AREA")
        op.type = "AREA"
        spl = box.split()
        op = spl.operator("object.light_add", text="Sun", icon="LIGHT_SUN")
        op.type = "SUN"
        op = spl.operator("object.light_add", text="Spot", icon="LIGHT_SPOT")
        op.type = "SPOT"
        # Right -- CubeMaps
        box = pie.split().column()
        box.label(text="Light Probes")
        op = box.operator("object.lightprobe_add", text="Irradiance Volume", icon="LIGHTPROBE_GRID")
        op.type = "GRID"
        spl = box.split()
        op = spl.operator("object.lightprobe_add", text="Cube", icon="LIGHTPROBE_CUBEMAP")
        op.type = "CUBEMAP"
        op = spl.operator("object.lightprobe_add", text="Plane", icon="LIGHTPROBE_PLANAR")
        op.type = "PLANAR"
        # Bottom -- Camera
        pie.operator("object.smart_add_camera", text="Add Camera", icon="CAMERA_DATA")

        # Top -- Images as Planes
        pie.operator("import_image.to_plane", text="Image as Plane", icon="FILE_IMAGE")
        # Text
        pie.operator("object.text_add", text="Text", icon="SMALL_CAPS")
        # Mannequin
        pie.operator("mesh.primitive_mannequin_add", text="Mannequin", icon="OUTLINER_OB_ARMATURE")
        # Armature
        pie.menu("PIE_MT_add_armature_extended", text="Armature", icon="ARMATURE_DATA")
        # Metaball
        pie.menu("VIEW3D_MT_metaball_add", text="Metaball", icon="META_DATA")


classes = (
    PIE_MT_AddMesh,
    PIE_MT_PhysicsSubPie,
    PIE_MT_MeshSubPie,
    PIE_MT_NormalSubPie,
    PIE_MT_AddModifier,
    PIE_MT_AddOtherObjects,
    PIE_MT_add_armature_extended,
)

kms = [
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "3D View",
        "letter": "A",
        "shift": 1,
        "ctrl": 0,
        "alt": 0,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_AddMesh"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "3D View",
        "letter": "Q",
        "shift": 1,
        "ctrl": 1,
        "alt": 0,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_AddModifier"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "A",
        "shift": 1,
        "ctrl": 0,
        "alt": 0,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_AddMesh"},
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "3D View",
        "letter": "A",
        "shift": 1,
        "ctrl": 1,
        "alt": 0,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_AddOtherObjects"},
    },
]
from my_pie_menus import utils


def register():
    utils.register_classes(classes)
    utils.register_keymaps(kms)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        utils.unregister_keymaps(kms)
