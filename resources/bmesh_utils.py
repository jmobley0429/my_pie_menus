import bpy
import bmesh

def get_sel_edges(bm):
    return [edge for edge in bm.edges[:] if edge.select]

def is_interior(edge):
    return len([face for face in edge.link_faces if face.select]) > 1

def get_bmesh(context):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')
    obj = context.edit_object
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    return bm

def cleanup_bmesh(cls):
        cls.bm.free()
        del cls.bm