# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 17:09:46 2020

@author: admin
"""

import sys
import math
import os
from typing import *
try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

from utils.configure_paths import configure_paths
configure_paths()
#move to scene_manager

from mathutils import Vector



def create_no_shadow_sun_lamp(location, rotation_euler, energy = 1):
    # Add another light source so stuff facing away from light is not completely dark
    light_data = bpy.data.lights.new(name="sunlight", type='SUN')
    light_data.use_shadow = False
    light_data.energy = energy
    light_object = bpy.data.objects.new(name="sunlight", object_data=light_data)
    light_object.location = location
    light_object.rotation_euler = tuple(math.radians(_) for _ in rotation_euler)
    # link light object
    bpy.context.collection.objects.link(light_object)
    
    # make it active 
    bpy.context.view_layer.objects.active = light_object


def auto_smooth_obj(obj):
    obj.data.use_auto_smooth = 1
    obj.data.auto_smooth_angle = math.pi/5 
    bpy.ops.object.shade_smooth()
    
    
def get_current_scene_key():
    '''
    Gets the current scene key
    '''
    return bpy.data.scenes.keys()[0]

def get_current_scene():
    return bpy.data.scenes[get_current_scene_key()]

def remove_default_cube():
    '''
    Removes the cube which is included by default when a new scene is created
    '''
    if "Cube" in bpy.data.meshes:
        mesh = bpy.data.meshes["Cube"]
        print("removing mesh", mesh)
        bpy.data.meshes.remove(mesh)

#move to scene_manager
def remove_default_camera():
    '''
    Removes the camera which is included by default when a new scene is created
    '''
    deselect_all()
    if "Camera" in bpy.data.objects:
        bpy.data.objects['Camera'].select_set(True)
        bpy.ops.object.delete() 

def deselect_all():
    bpy.ops.object.select_all(action='DESELECT')

def set_animation_frame(frame_no, scene = None, verbose = False):
    if not scene:
        scene = get_current_scene()
        
    #should check scene is valid...
    scene.frame_set(frame_no)
    bpy.context.view_layer.update()
    print("Set frame to ", frame_no)

def get_start_animation_frame(scene = None):
    if not scene: 
        scene = get_current_scene()
    return scene.frame_start

def get_end_animation_frame(scene = None):
    if not scene: 
        scene = get_current_scene()
    return get_keyframes_of_imported()[-1]
    #return scene.frame_end

# get keyframes of object list
def get_keyframes(obj_list):
    keyframes = []
    for obj in obj_list:
        anim = obj.animation_data
        if anim is not None and anim.action is not None:
            for fcu in anim.action.fcurves:
                for keyframe in fcu.keyframe_points:
                    x, y = keyframe.co
                    if x not in keyframes:
                        keyframes.append((math.ceil(x)))
    return keyframes

def get_keyframes_of_imported():
    imported_obj = bpy.data.objects
    keys = get_keyframes(imported_obj)
    return keys

def select_objects_by_type(object_type: str, scene = None):
    assert object_type in ["Mesh", "Light", "Light Probe", "Camera", "Speaker", "Surface", "Armature", "Empty", "Image"]
    bpy.ops.object.select_all(action='DESELECT')    
    
    for scene_object in get_objects_by_type(object_type, scene):
        scene_object.select = True
                
def get_objects_by_type( object_type: str, scene = None) -> List:
    return_objects = []
    
    if not scene:
        #assume using the open scene
        scene = bpy.context.scene
        
    for ob in scene.objects:
        # make the current object active and select it
        #scene.objects.active = ob
        ob.select_set(state=True)
        bpy.context.view_layer.objects.active = ob
    
        # make sure that we only export meshes
        if ob.type == object_type:
            return_objects.append(ob)
    return return_objects

def remove_default_light():
    #deselect all to prevent accidental delation of other things
    deselect_all()
    if "Light" in bpy.data.objects:
        bpy.data.objects['Light'].select_set(True)
        bpy.ops.object.delete() 
        

def set_empty_scene(verbose = False):
    scene = bpy.context.scene
    if verbose:
        for c in scene.collection.children:        
            print("Unlinking {} from the scene.".format(c.name))
            scene.collection.children.unlink(c)
    else:
        for c in scene.collection.children:
            scene.collection.children.unlink(c)
    #bpy.context.scene.update()
    
    
def reset_blend():
    #bpy.ops.wm.read_factory_settings()

    for scene in bpy.data.scenes:
        for obj in scene.objects:
            bpy.context.collection.objects.unlink(obj)

    # only worry about data in the startup scene
    for bpy_data_iter in (
            bpy.data.objects,
            bpy.data.meshes,
            bpy.data.cameras,
            ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data)

def delete_hierarchy(parent_obj):
    '''
    For a given selected object, deletes associated hierarchy
    :return:
    '''

    bpy.ops.object.select_all(action='DESELECT')
    obj = bpy.data.objects[parent_obj]
    obj.animation_data_clear()
    names = set()
    def get_child_names(obj):
        for child in obj.children:
            names.add(child.name)
            if child.children:
                get_child_names(child)

    get_child_names(obj)
    print(names)
    objects = bpy.data.objects
    #[setattr(objects[n], 'select', True) for n in names]
    for name in names:
        print("selecting: ", name)
        bpy.data.objects[name].select_set(True)

    # Remove the animation from the all the child objects
    for child_name in names:
        bpy.data.objects[child_name].animation_data_clear()

    result = bpy.ops.object.delete()
    if result == {'FINISHED'}:
        print("Successfully deleted object")
    else:
        print("Could not delete object")


def get_local_bounding_box_center(obj):
    return 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())

def get_global_bounding_box_center(obj):
    return obj.matrix_world @ get_local_bounding_box_center(obj)

def get_scales(obj, max_width) -> List[float]:
    '''Returns a list of scaling coefficients to limit the obj bounding box to max_width'''
    bbox = obj.bound_box
    print("bbox: ", [_ for _ in bbox])
    return [max_width/(max([coord[xyz_index] for coord in bbox]) - min([coord[xyz_index] for coord in bbox])) for xyz_index in range(3)]


def get_min_scaling_coeff(obj, max_width) -> float:
    '''Returns the minimum scaling coefficient that can be used scale obj uniformly to fit into a box with dimensions [-max_width/2, max_width/2] on each axis '''
    return min(get_scales(obj, max_width))

def scale_obj(obj, scale)->None:
    '''Uniformly scales an object along x,y,z axes'''
    obj.scale = (scale, scale, scale)


def translate_obj(obj, offset) -> None:
    '''Translates an object be the given offset'''
    obj.location -= offset
