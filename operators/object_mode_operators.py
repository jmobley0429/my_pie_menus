import bpy
import bmesh
import math
import json
import re
from mathutils import Euler

from pathlib import Path

from .custom_operator import CustomOperator


class AddCameraCustom(bpy.types.Operator):
    bl_idname = "object.smart_add_camera"
    bl_label = "Smart Add Camera"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.camera_add(
            enter_editmode=False,
            align='VIEW',
            location=(0, 0, 0),
            rotation=(1.33911, 0.0142096, -0.524513),
            scale=(1, 1, 1),
        )
        bpy.ops.view3d.camera_to_view()
        return {'FINISHED'}


class AddLightSetup(CustomOperator, bpy.types.Operator):
    bl_idname = "object.add_light_setup"
    bl_label = "Add 3-Point Lighting Setup"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def _get_last_light():
        lights.append(bpy.data.objects[-1])

    @staticmethod
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

    def execute(self, context):
        obj = self.get_active_obj()
        bpy.ops.object.empty_add(type="CIRCLE", location=obj.location)
        track_obj = self.get_active_obj()
        track_obj.name = "Tracker"

        obj_w, obj_d, obj_h = obj.dimensions
        ox, oy, oz = obj.location

        key_loc = obj.dimensions.copy() * 1.2
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

        lights = []
        self.add_light(
            key_loc, name="Key", energy=key_power, target_obj=track_obj, color=(1, 0.94, 0.88), size=key_size
        )
        _get_last_light()
        self.add_light(
            fill_loc, name="Fill", energy=fill_power, target_obj=track_obj, color=(0.33, 0.80, 1), size=fill_size
        )
        _get_last_light()
        self.add_light(
            rim_loc, name="Rim", energy=rim_power, target_obj=track_obj, color=(0.33, 0.80, 1), size=rim_size
        )
        _get_last_light()

        for l in lights:
            l.parent = track_obj

        return {'FINISHED'}

    def menu_func(self, context):
        self.layout.operator(self.bl_idname, text=self.bl_label)


class SetCustomBatchName(bpy.types.Operator):

    bl_idname = "object.set_custom_batch_name"
    bl_label = "Set Custom Batch Name"

    name_string: bpy.props.StringProperty(name="New Name")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        objs = context.selected_objects
        for obj in objs:
            obj.name = self.name_string
        for obj in objs:
            obj.name = obj.name.replace('.0', "_")
        return {'FINISHED'}


class JG_SetUVChannels(bpy.types.Operator):

    bl_idname = "object.jg_set_uv_channels"
    bl_label = "Set JG UV Channels"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        objs = context.selected_objects
        obj_data = []
        for obj in objs:
            bpy.context.view_layer.objects.active = obj
            mesh = obj.data
            uvs = mesh.uv_layers
            for i, u in enumerate(uvs):
                if i > 0:
                    mesh.uv_layers.active_index = i
                    bpy.ops.mesh.uv_texture_remove()

        for obj in objs:
            mesh = obj.data
            if mesh not in obj_data:
                obj_data.append(mesh)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.mesh.uv_texture_add()
                uvs = mesh.uv_layers
                for i, u in reversed(list(enumerate(uvs))):
                    name = f"UV_Channel_{i+1}"
                    u.name = name
            else:
                continue

        return {'FINISHED'}


classes = (
    AddCameraCustom,
    AddLightSetup,
    SetCustomBatchName,
    # delete later
    JG_SetUVChannels,
)