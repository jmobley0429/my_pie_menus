import bpy
import bmesh

def get_sel_edges(bm):
    return [edge for edge in bm.edges[:] if edge.select]

def is_interior(edge):
    return len([face for face in edge.link_faces if face.select]) > 1