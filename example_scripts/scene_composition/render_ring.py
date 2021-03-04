# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 16:00:35 2020

@author: admin
"""

import math
import sys
import os
from typing import *
import importlib


try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

from utils.configure_paths import configure_paths
configure_paths()


#from blender-cli-rendering.utils.utils import build_rgb_background, build_environment_texture_background, add_track_to_constraint, clean_objects
#from blender-cli-rendering.utils.composition import build_scene_composition
#from blender-cli-rendering.utils.mesh import create_plane
#from blender-cli-rendering.utils.lighting import create_sun_light
#import blender-cli-rendering.external.cc0assetsloader as loader

from camera_manager.camera_manager import (create_camera_ring, get_all_cameras, use_eevee, render_still_image, set_res, get_camera_azimuth,
                                           get_camera_elevation, get_camera_distance_to_object, set_transparent_background)
from format_converters.ImportExportParamManager import ImportArgsManager
from format_converters.converter import import_file
from scene_manager.scene_manager import set_animation_frame, scale_obj, get_min_scaling_coeff, translate_obj, get_global_bounding_box_center
from scene_manager.scene_manager import get_current_scene, reset_blend, create_no_shadow_sun_lamp, auto_smooth_obj
from blender_cli_rendering.utils.utils import clean_objects
def write_rendered_file_names(output_file_path: str, image_names: List):
    with open(output_file_path, "w") as f:
        f.write('\n'.join(image_names))

def write_rendered_file_metadata(output_file_path: str, azimuths: List, elevations: List, distances: List):
    assert len(azimuths) == len(distances) == len(elevations)
    with open(output_file_path, "w") as f:
        for azimuth, elevation, distance in zip(azimuths, elevations, distances):
            f.write("{}, {}, {}\n".format(azimuth, elevation, distance))


def run_main():
    #reset_blend()
    clean_objects()

    #create a marble floor plane
    #loader.build_pbr_textured_nodes_from_name("Marble01")
    #current_object = create_plane(size=20.0, name="Floor")
    #current_object.data.materials.append(bpy.data.materials["Marble01"])

    #add a sunlight
    #create_sun_light(rotation=(0.0, math.pi * 0.5, -math.pi * 0.1))

    #set hrd background image
    #hdri_path = r"C:\Users\admin\3DGeom\blender3dgscripts\blender-cli-rendering\assets\HDRIs\green_point_park_2k.hdr"
    #build_environment_texture_background(bpy.data.scenes["Scene"].world, hdri_path)
    #build_scene_composition(bpy.data.scenes["Scene"])


    #############A hack to first convert to gltf.#############
    fpath = r"data\render_ring_data\input\1a8bbf2994788e2743e99e0cae970928\model"
    #os.system("obj2gltf -i {fpath}.obj -o {fpath}.gltf".format(fpath = fpath))


    #importArgParser = ImportArgsManager("gltf")
    #importArgParser.set_import_arg("filepath", r"data\test_input\fbx\Capoeira.fbx")
    #importArgParser.set_import_arg("filepath", r"data\render_ring_data\input\1a8bbf2994788e2743e99e0cae970928\model.gltf")


    #keep all vertices as one onbject for scaling
    #importArgParser.set_import_arg("use_split_objects", False)

        #############A hack to first convert to gltf.#############

    previously_selected_objects = set(bpy.context.selected_objects)

    import_file_location = r"data/render_ring_data/input/1a6f615e8b1b5ae4dbbc9440457e303e/models/model_normalized.obj"
    importArgParser = ImportArgsManager("obj")
    importArgParser.set_import_arg("filepath", import_file_location)
    import_file(import_file_location, importArgParser.get_import_args_dict())

    importArgParser.set_import_arg("use_split_objects", False)
    #importArgParser.set_import_arg("use_edges", False)
    #importArgParser.set_import_arg("use_smooth_groups", True)
    #importArgParser.set_import_arg("use_split_groups", True)
    #importArgParser.set_import_arg("use_image_search", True)
    #importArgParser.set_import_arg("use_groups_as_vgroups", False)
    #importArgParser.set_import_arg("split_mode", "ON")
    #importArgParser.set_import_arg("split_mode", "ON




    #bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='SELECT')

    # return all currently selected objects
    selected_objs = list(set(bpy.context.selected_objects) - previously_selected_objects)
    #bpy.ops.object.join()
    #_correct_materials(selected_objs)

    imported_obj = bpy.context.selected_objects[0]

    max_width = 0.9
    scale_obj(imported_obj, get_min_scaling_coeff(imported_obj, max_width))
    translate_obj(imported_obj, get_global_bounding_box_center(imported_obj))


    auto_smooth_obj(imported_obj)

    create_no_shadow_sun_lamp((2,0,0), rotation_euler = (0,90,0))
    create_no_shadow_sun_lamp((0,0,2), rotation_euler = (0,0,0))

    create_no_shadow_sun_lamp((-2,0,0), rotation_euler = (0,-90,0))
    create_no_shadow_sun_lamp((0,0,-2), rotation_euler = (180,0,0))


    create_camera_ring(1.8, 3, 0)


    use_eevee()
    set_res(128, 128)
    set_transparent_background()
    output_base_path = r"\data\render_ring_data\output\1a6f615e8b1b5ae4dbbc9440457e303e"
    output_text_file_path = output_base_path + r"\renderings.txt"
    ouput_metadata_file_path = output_base_path + r"\rendering_metadata.txt"

    rendered_file_names = []
    azimuths, elevations, distances = [], [], []
    for index, camera in enumerate(get_all_cameras()):
        file_name = r"\{:02d}".format(index) + ".png"
        render_still_image(os.getcwd() + output_base_path + file_name, camera, verbose = True)
        rendered_file_names.append(file_name)
        azimuths.append(get_camera_azimuth(camera))
        elevations.append(get_camera_elevation(camera))
        distances.append(get_camera_distance_to_object(camera, imported_obj))

    write_rendered_file_names(output_text_file_path, rendered_file_names)
    write_rendered_file_metadata(ouput_metadata_file_path, azimuths, elevations, distances)

if __name__ == '__main__':
    run_main()
    '''
    post render functions
    
    #for frame in range(1,31, 10):
    #    for index, camera in enumerate(get_all_cameras()):
    #        print("rendering camera {} frame {}".format(index, frame))
    #        set_animation_frame(frame)
    #        render_still_image(os.getcwd() + r"\data\test_output\png\capoeira\camera_{}frame_{}.png".format(index, frame), camera, verbose = True)
    
    
            
    '''
            
            
            
            
            
            
            
            
            
            
            
            
            
            
