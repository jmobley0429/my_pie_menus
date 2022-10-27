import bpy
import bmesh
import math
import json
from mathutils import Euler
from collections import defaultdict
import numpy as np
import platform



def is_linux():
    return "linux" in platform.system().lower()

def convert_bbox_to_world(bbox, mx):
    num_points = len(bbox)
    coords_4d = np.ones((num_points, 4), 'f')
    coords_4d[:, :-1] = bbox
    return np.einsum('ij,aj->ai', mx, coords_4d)[:, :-1]


def get_bbox_center(obj, matrix_world):
    bounds = np.array([v[:] for v in obj.bound_box])
    ws_bbox = convert_bbox_to_world(bounds, matrix_world)
    return ws_bbox.sum(0) / len(bounds)


def get_active_obj():
    return bpy.context.active_object


def clamp(value, min_num, max_num):
    return min(max_num, max(min_num, value))


def get_loc_matrix_from_cursor(self, context):
    rot = Quaternion((1.0, 0.0, 0.0, 0.0))
    scale = Vector((1.0, 1.0, 1.0))
    loc = context.scene.cursor.matrix.translation
    return Matrix().LocRotScale(loc, rot, scale)


def set_parent(obj, parent_obj, keep_offset=False):
    orig_loc = obj.matrix_world.translation.copy()
    obj.parent = parent_obj
    if not keep_offset:
        obj.matrix_world.translation = orig_loc


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

def get_blender_version():
    return ".".join(bpy.app.version_string.split('.')[:-1])
    


def register_keymaps(kms, addon_keymaps):
    if kms or kms is not None:
        for keymap in kms:
            keymap_operator = keymap.pop("keymap_operator")
            name = keymap.pop("name")
            letter = keymap.pop("letter")
            shift = keymap.pop("shift")
            ctrl = keymap.pop("ctrl")
            alt = keymap.pop("alt")
            space_type = keymap.pop("space_type")
            region_type = keymap.pop("region_type")
            keywords = keymap.pop('keywords')

            wm = bpy.context.window_manager
            kc = wm.keyconfigs.addon
            if kc:
                # existing_kmis = get_existing_keymap_items(name)
                km = wm.keyconfigs.addon.keymaps.new(name=name)
                print(km)
                kmi = km.keymap_items.new(keymap_operator, letter, 'PRESS', ctrl=ctrl, alt=alt, shift=shift)
                # str_vers = kmi.to_string()
                kmi.active = True
                # for ekmi in existing_kmis:
                #     if str_vers == ekmi.to_string():
                #         ekmi.active = False

                for kw, value in keywords.items():
                    setattr(kmi.properties, kw, value)
                addon_keymaps.append((km, kmi))


def register_classes(classes):
    for cls in classes:
        print(cls)
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            bpy.utils.unregister_class(cls)
            bpy.utils.register_class(cls)


def unregister_keymaps(addon_keymaps):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()

def get_or_create_collection(name:str ) -> bpy.types.Collection:
    '''Attempts to return the collection with a given name, creates one if the collection doesn't exist.'''
    try:
        return bpy.data.collections[name]
    except KeyError:
        return  bpy.data.collections.new(name) 
    
def link_collection(coll:bpy.types.Collection,  scene="Scene"):
    '''Attempts to link collection to scene collection, if collection already linked, will pass.'''
    scene = bpy.data.scenes[scene]
    try:
        scene.collection.children.link(coll)
    except RuntimeError:
        pass

def find_layer_collection(collection:bpy.types.Collection, scene="Scene", view_layer="ViewLayer") -> bpy.types.LayerCollection:
    '''Takes a Collection object and returns the corresponding LayerCollection object from the scene.'''
    scene = bpy.data.scenes[scene]
    for c in scene.view_layers[view_layer].layer_collection.children[:]:
        if c.name == collection.name:
            return c

def get_objs_from_coll(coll, type="MESH"):
    return [obj for obj in coll.objects if obj.type == type]