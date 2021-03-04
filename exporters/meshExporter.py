# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 12:30:46 2020

@author: admin
"""

import sys
import os
from typing import *
from inspect import signature


try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

sys.path.append('.')
from utils.configure_paths import configure_paths
configure_paths()

from format_converters.converter import SceneFormatExporter, valid_formats, get_import_fn_args_dict,get_export_fn_args_dict , conversion_types, get_file_ext, get_folder, export_file
from format_converters.ImportExportParamManager import fbx2objArgParser, ImportExportArgManager, ExportArgsManager
from scene_manager.scene_manager import set_empty_scene, set_animation_frame, get_start_animation_frame, get_end_animation_frame
#def import_file(importArgsManager: ImportArgsManager):
#    conversion_function = get_conversion_function(ImportArgsManager.import_file_type)
    
    
        
class ExportFramesAsMesh:
    '''
    Assuming an animation has already been imported into blender, exports given frames as meshes
    ''' 
        
    def __init__(self):
        
        #self.importer = 
        self.exporter = SceneFormatExporter()
        
    def list_kwargs(self):
        return self.importExportArgManager.get_available_args()

    
    def exportFirstFrameAsMesh(self, export_file_loc, scene = None, export_kw_args: dict = None, individual_meshes = False, verbose: bool = False):
        '''
        Renders first frame only of given scene
        '''
        #self.import_kwargs["use_animation"] = False
        #self.import_kwargs["filepath"] = import_file_loc
        #self.importExportArgManager.set_import_arg("use_animation", False)
        assert export_file_loc in conversion_types["mesh"], "The export file must be of type " + get_file_ext(export_file_loc)
        set_animation_frame(1)
        self.exportAnimationFramesAsMesh(get_folder(export_file_loc))
        
    def exportAnimationFramesAsMesh(self, export_folder_loc: str, export_base_name: str, export_file_ext:str, export_kw_args: dict = None, individual_meshes = False, start_frame = 1, end_frame = 1, step = 1, all_frames = False, verbose = False):
        '''
        Converts an animation to a sequence of obj files frame-by-frame. Assumes the scene has already been imported and set up.
        '''
        #set_empty_scene(verbose = True)
        #self.importExportArgManager.set_import_arg("filepath", import_file_loc)
        #import_file(import_file_loc, self.importExportArgManager.get_import_args_dict(), verbose)

        assert export_file_ext in conversion_types["mesh"] + conversion_types["scene"], "The export file must be of type {}, not {}".format(conversion_types["mesh"] + conversion_types["scene"], export_file_ext)
        self.exportArgManager = ExportArgsManager(export_file_type = export_file_ext)

        
        if export_kw_args:
            for key, value in export_kw_args.items():
                self.exportArgManager.set_export_arg(key, value)
                    
            
        self.exportArgManager.set_export_arg("filepath",  export_folder_loc)
        self.exportArgManager.set_export_arg("use_materials", True)
        self.exportArgManager.set_export_arg("path_mode", "COPY")
        if all_frames:
            self.exportArgManager.set_export_arg("use_animation", True)
            self.exportArgManager.set_export_arg("filepath", export_folder_loc + "\\{}.{}".format(export_base_name, export_file_ext))
            self.exporter.export_scene(export_folder_loc + "\\{}.{}".format(export_base_name, export_file_ext), self.importExportArgManager.get_export_args_dict())
            
        else:
            #scene = get_current_scene()
            assert start_frame >= get_start_animation_frame(), "Start frame must be > {}".format(get_start_animation_frame())
            assert end_frame <= get_end_animation_frame(), "End frame must be < {}".format(get_end_animation_frame())
            print("Saving frames {} to {} as {}".format(start_frame, end_frame, export_file_ext))
            for frame_no in range(start_frame, end_frame + 1, step):
                set_animation_frame(frame_no)
                self.exportArgManager.set_export_arg("filepath", export_folder_loc+ "\\{}_{}.{}".format(export_base_name, frame_no, export_file_ext))
                if verbose:
                    print("Exporting frame ", frame_no)
                self.exporter.export_scene(export_folder_loc+ "\\{}_{}.{}".format(export_base_name, frame_no,export_file_ext), self.exportArgManager.get_export_args_dict(), export_file_ext)

def export_texture_files(dir_to_export_to, png_or_jpg):
    '''
    Exports texture files for given selection
    '''
    exportArgManager = ExportArgsManager(export_file_type = "gltf")
    exportArgManager.set_export_arg("export_image_format", "AUTO")
    exportArgManager.set_export_arg("export_texture_dir", ".")
    exportArgManager.set_export_arg("filepath", dir_to_export_to + "\\temp.gltf")
    exportArgManager.set_export_arg("export_format", "GLTF_SEPARATE")
    
    exportArgManager.set_export_arg("export_draco_mesh_compression_enable", True)
    exportArgManager.set_export_arg("export_draco_mesh_compression_level", 6)
    export_file(dir_to_export_to + "\\temp.gltf", exportArgManager.get_export_args_dict(), verbose = True)
    os.remove(dir_to_export_to + "\\temp.bin")
        
if __name__ == '__main__':
    pass

    
    
    
    
    
    
    
    
    
    
    