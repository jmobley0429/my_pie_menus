import bpy
import bmesh
import math
import json
from mathutils import Euler


def get_active_obj():
    return bpy.context.active_object


def clamp(value, min_num, max_num):
    return min(max_num, max(min_num, value))
