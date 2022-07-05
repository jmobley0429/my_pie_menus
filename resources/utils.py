import bpy
import bmesh
import math
import json
from mathutils import Euler


def get_active_obj():
    return bpy.context.active_object


def clamp(value, min_num, max_num):
    return min(max_num, max(min_num, value))


def get_loc_matrix_from_cursor(self, context):
    rot = Quaternion((1.0, 0.0, 0.0, 0.0))
    scale = Vector((1.0, 1.0, 1.0))
    loc = context.scene.cursor.matrix.translation
    return Matrix().LocRotScale(loc, rot, scale)
