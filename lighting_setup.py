import bpy
from bpy import context as C, data as D, ops as O

lights = [l for l in bpy.data.objects if l.type == "LIGHT"]
for l in lights:
    C.view_layer.objects.selected = l
    O.object.delete()


obj = bpy.data.objects['Suzanne']
C.view_layer.objects.active = obj


def last_light():
    return bpy.data.lights[:][0]


def last_constraint(obj):
    return obj.constraints[0]


def add_light(location, name, energy, target_obj, color, size):
    bpy.ops.object.light_add(type="AREA", location=location)
    key = last_light()
    key.name = name
    key.energy = energy
    key.color = color
    key.size = size
    light_obj = bpy.context.objectz
    light_obj.constraints.new(type="TRACK_TO")
    mod = last_constraint(light_obj)
    mod.target = obj


obj = C.active_object
obj_w, obj_d, obj_h = obj.dimensions
ox, oy, oz = obj.location

bpy.ops.object.add(type="EMPTY", location=obj.location)
track_obj = bpy.context.active_object

key_loc = obj.dimensions.copy() * 1.2
print(obj.dimensions)
key_loc.y *= -1
key_size = obj.dimensions.x * 0.75
key_power = 125


fill_loc = key_loc.copy() * 1.2
fill_loc.x *= -1
fill_loc.z *= 0.5
fill_size = key_size * 2.5
fill_power = key_power * 0.5

rim_loc = key_loc.copy().cross(obj.location) * 0.75
rim_loc.z *= 0.1
rim_loc.y *= -1
rim_power = key_power * 2
rim_size = key_size * 0.3
rim_color = (1, 1, 1)

add_light(key_loc, name="Key", energy=key_power, target_obj=track_obj, color=(1, 0.94, 0.88), size=key_size)

add_light(fill_loc, name="Fill", energy=fill_power, target_obj=track_obj, color=(0.33, 0.80, 1), size=fill_size)

add_light(rim_loc, name="Rim", energy=rim_power, target_obj=track_obj, color=(0.33, 0.80, 1), size=rim_size)
