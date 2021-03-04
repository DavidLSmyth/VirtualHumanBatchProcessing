# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 11:46:47 2020

@author: admin

Contains all common camera related functionality
"""

import os
import sys
import math
from typing import *
from mathutils import Matrix
import numpy as np
top_level = __import__(__name__.split('.')[0])

try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

from ..utils.configure_paths import configure_paths
configure_paths()

from ..scene_manager.scene_manager import get_current_scene, set_empty_scene
 


######
#Be careful, blender does some memory management behind the scenes. Holding direct references to objects can cause problems
#instead try and use indices or names
#####

def get_all_cameras():
    '''
    Returns all cameras in the scene. There are 2 types: data cameras and object cameras.
    '''
    cam_list_names = [cam.name for cam in list(bpy.data.cameras)]
    #print(cam_list_names)
    #print("Found objects: ", [camera.name for camera in bpy.data.objects ])
    cam_list = [camera for camera in bpy.data.objects if camera.name in cam_list_names]
    #print("Found the following cameras: ", cam_list)
    #cam_list = bpy.data.collections['Cameras']
    #cam_list = bpy.data.objects["Camera"]
    return cam_list
    #camidx = 0
    #camobj, camdat = camobj_list[camidx], camdat_list[camidx]

    #return bpy.data.objects["Camera"]

def set_active_camera_in_scene(camera, scene_key):
    bpy.data.scenes[scene_key].camera = camera
    
def set_scene_camera(camera):
    bpy.data.scenes

def get_intrinsic_params(camera):
    pass

def get_extrinsic_params(camera):
    pass

def get_camera_by_name():
    pass

def set_transparent_background():
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'

def move_camera_to_location(camera, location):
    camera.location = location

def get_camera_intrinsics(camd):
    f_in_mm = camd.lens
    scene = bpy.context.scene
    resolution_x_in_px = scene.render.resolution_x
    resolution_y_in_px = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100
    sensor_width_in_mm = camd.sensor_width
    sensor_height_in_mm = camd.sensor_height
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
    if (camd.sensor_fit == 'VERTICAL'):
        # the sensor height is fixed (sensor fit is horizontal),
        # the sensor width is effectively changed with the pixel aspect ratio
        s_u = resolution_x_in_px * scale / sensor_width_in_mm / pixel_aspect_ratio
        s_v = resolution_y_in_px * scale / sensor_height_in_mm
    else: # 'HORIZONTAL' and 'AUTO'
        # the sensor width is fixed (sensor fit is horizontal),
        # the sensor height is effectively changed with the pixel aspect ratio
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
        s_u = resolution_x_in_px * scale / sensor_width_in_mm
        s_v = resolution_y_in_px * scale * pixel_aspect_ratio / sensor_height_in_mm

    # Parameters of intrinsic calibration matrix K
    alpha_u = f_in_mm * s_u
    alpha_v = f_in_mm * s_v
    u_0 = resolution_x_in_px*scale / 2
    v_0 = resolution_y_in_px*scale / 2
    skew = 0 # only use rectangular pixels

    K = Matrix(
        ((alpha_u, skew,    u_0),
        (    0  ,  alpha_v, v_0),
        (    0  ,    0,      1 )))

    K_serializable = np.array(((alpha_u, skew,    u_0),
        (    0  ,  alpha_v, v_0),
        (    0  ,    0,      1 )))
    return K_serializable.tolist()



#azimuth, elevation, and distance
def get_camera_azimuth(camera):
    '''
    returns the camera azimuth in relation to positive z-axis
    '''
    return math.degrees(camera.rotation_euler.z) % 360

def get_camera_elevation(camera):
    return math.degrees(camera.rotation_euler.y)

def get_camera_distance_to_object(camera, object):
    return (camera.matrix_world.translation - object.matrix_world.translation).length
    

def rotate_camera(camera, x_rotation, y_rotation, z_rotation):
    camera.rotation_euler.x = x_rotation
    camera.rotation_euler.y = y_rotation
    camera.rotation_euler.z = z_rotation
    


    
def get_camera_rotations_positions_on_circle(circle_radius, num_angles, z_offset) -> float:
    '''Returns a generator containing (rotation, position) pairs, which can be used to update a camera position to track the origin around a circle.'''
    rotAngle  = 360 / num_angles
    for camera_pos_index in range(num_angles):
        angle = camera_pos_index * rotAngle
        #camera_object.rotation_euler.z = radians( angle )
        z_rotation_radians = math.radians(angle)
        camera_location = (circle_radius  * math.cos(z_rotation_radians), circle_radius * math.sin(z_rotation_radians), z_offset)
#        camera_object.location = (radius * math.cos( radians(angle)), radius * math.sin(radians(angle)), 0)
        #yield z_rotation_radians, camera_location
        yield z_rotation_radians, camera_location
        #yield camera_location

def create_camera_ring(radius, no_cameras, z_offset):
    index = 0
    for rotation, location in get_camera_rotations_positions_on_circle(radius, no_cameras, z_offset):
        create_camera_at_location_with_rotation_z(location, rotation, "ring_camera_"+str(index))
        index += 1
        
        

def set_camera_location(camera, location):
    #error checking
    camera.location = location

def set_lens_type(camera, lens_type: str):
    assert lens_type in ["perspective", ""]

def create_camera_at_location_with_rotation_z(location: Tuple[float, float, float], euler_rotation_z, name: str):
    bpy.ops.object.camera_add(location = location, rotation = (math.radians(90),math.radians(0),math.radians(90) + euler_rotation_z))
    bpy.context.view_layer.update()
    #update both object and data
    bpy.context.object.name = name
    bpy.context.object.data.name = name
    bpy.context.view_layer.update()

    #bpy.context.object.rotation_euler.z = euler_rotation_z
    #return new_cam    

    
def set_camera_resolution():
    pass

def set_animation_track():
    pass

def _render(animation = False, write_still = False, ):
    bpy.ops.render.render(animation)
    
def use_eevee():
    bpy.context.scene.render.engine = "BLENDER_EEVEE"

def set_render_file_path(filepath):
    bpy.context.scene.render.filepath = filepath
    
def set_fps(fps):
    bpy.context.scene.render.fps = fps
    
    
def set_res(res_x, res_y):
    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y
    
def set_no_rendering_threads(no_threads):
    bpy.context.scene.render.thread = no_threads
    

def render_still_image(file_path, camera, file_extension = "PNG", verbose = False):
    assert file_extension in ('BMP', 'IRIS', 'PNG', 'JPEG', 'JPEG2000', 'TARGA', 'TARGA_RAW', 'CINEON', 'DPX', 'OPEN_EXR_MULTILAYER', 'OPEN_EXR', 'HDR', 'TIFF', 'AVI_JPEG', 'AVI_RAW', 'FRAMESERVER', 'H264', 'FFMPEG', 'THEORA', 'XVID')
    #make sure camera is selected
    bpy.context.scene.camera = camera
    bpy.context.scene.render.image_settings.file_format = file_extension
    bpy.context.scene.render.filepath = file_path
    if verbose:
        print("Rendering using camera " + camera.name)
    bpy.ops.render.render(write_still = True)

def use_persistent_data(true_false):
    '''
    Keep render data around for faster re-renders
    '''
    bpy.context.scene.render.use_persistent_data = true_false

def render_animation(file_format, file_path, start_frame, end_frame, fps, use_eevee = False):
    pass



if __name__ == "__main__":
    set_empty_scene()
    create_camera_ring(8, 12)
    
