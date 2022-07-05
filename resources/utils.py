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
