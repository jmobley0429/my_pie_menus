import bpy
import bmesh
import math
import json
from mathutils import Euler
from collections import defaultdict


def get_active_obj():
    return bpy.context.active_object


def clamp(value, min_num, max_num):
    return min(max_num, max(min_num, value))


def get_loc_matrix_from_cursor(self, context):
    rot = Quaternion((1.0, 0.0, 0.0, 0.0))
    scale = Vector((1.0, 1.0, 1.0))
    loc = context.scene.cursor.matrix.translation
    return Matrix().LocRotScale(loc, rot, scale)


def write_mesh_data_to_json(obj, file_name=""):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    data = defaultdict(list)
    data["vertices"] = [tuple(v.co) for v in bm.verts[:]]

    for e in bm.edges[:]:
        edge_verts = [v.index for v in e.verts[:]]
        data['edges'].append(edge_verts)
    for f in bm.faces[:]:
        face_verts = [v.index for v in f.verts[:]]
        data['faces'].append(face_verts)

    with open(file_name, "w") as f:
        json.dump(data, f)


def register_keymap(setting: dict, addon_keymaps: list) -> None:
    '''Takes a keymap dict in this format:
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "3D View",
        "letter": "A",
        "idname": "PIE_MT_AddMesh",
        "shift": 1,
        "ctrl": 0,
        "alt": 0,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
    }
    and creates a keymap item and keymapping.'''

    args = list(dict(sorted(setting.items())).values())
    alt, ctrl, idname, keymap_operator, letter, name, region_type, shift, space_type = args
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = kc.keymaps.new(name=name, space_type=space_type, region_type=region_type)
    kmi = km.keymap_items.new(keymap_operator, letter, 'PRESS', shift=shift, ctrl=ctrl, alt=alt)
    kmi.properties.name = idname
    kmi.active = True
    addon_keymaps.append((km, kmi))


def unregister_keymaps(addon_keymaps):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
            kc.keymaps.remove(km)
    addon_keymaps.clear()
