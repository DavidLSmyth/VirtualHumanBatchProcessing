# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 16:00:35 2020

@author: admin
"""

import math
import sys
import os

try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

sys.path.append('.')
from utils.configure_paths import configure_paths
configure_paths()


from blender_cli_rendering.utils.utils import build_rgb_background, build_environment_texture_background, add_track_to_constraint, clean_objects
from blender_cli_rendering.utils.composition import build_scene_composition
from blender_cli_rendering.utils.mesh import create_plane
from blender_cli_rendering.utils.lighting import create_sun_light
import blender_cli_rendering.external.cc0assetsloader as loader

from camera_manager.camera_manager import create_camera_ring, get_all_cameras, use_eevee, render_still_image, set_res
from format_converters.ImportExportParamManager import ImportArgsManager
from format_converters.converter import import_file
from scene_manager.scene_manager import set_animation_frame
from scene_manager.scene_manager import get_current_scene, reset_blend


if __name__ == '__main__':
    #reset_blend()
    clean_objects()
    create_camera_ring(24, 4, 1)
    
    #create a marble floor plane
    #loader.build_pbr_textured_nodes_from_name("Marble01")
    #current_object = create_plane(size=20.0, name="Floor")
    #current_object.data.materials.append(bpy.data.materials["Marble01"])
    
    #add a sunlight
    #create_sun_light(rotation=(0.0, math.pi * 0.5, -math.pi * 0.1))
    
    #set hrd background image
    #hdri_path = r"C:\Users\admin\3DGeom\blender3dgscripts\blender_cli_rendering\assets\HDRIs\green_point_park_2k.hdr"
    build_environment_texture_background(bpy.data.scenes["Scene"].world, hdri_path)
    build_scene_composition(bpy.data.scenes["Scene"])
    
    importArgParser = ImportArgsManager("obj")
    #importArgParser.set_import_arg("filepath", r"data\test_input\fbx\Capoeira.fbx")
    importArgParser.set_import_arg("filepath", r"data\test_input\1a6f615e8b1b5ae4dbbc9440457e303e\1a6f615e8b1b5ae4dbbc9440457e303e\model.obj")
    #importArgParser.set_import_arg("filepath", r"data\test_input\fbx\Sitting_Laughing.fbx")
    import_file(r"data\test_input\1a6f615e8b1b5ae4dbbc9440457e303e\1a6f615e8b1b5ae4dbbc9440457e303e\model.obj", importArgParser.get_import_args_dict())
    use_eevee()
    set_res(64, 64)
    
    #should use pre and post render functions
    
    for frame in range(1,31, 10):
        for index, camera in enumerate(get_all_cameras()):
            print("rendering camera {} frame {}".format(index, frame))
            set_animation_frame(frame)
            render_still_image(os.getcwd() + r"\data\test_output\png\capoeira\camera_{}frame_{}.png".format(index, frame), camera, verbose = True)
    