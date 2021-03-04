import sys
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

from format_converters.converter import SceneFormatExporter, import_file, export_file, get_conversion_function, valid_formats, get_import_fn_args_dict,get_export_fn_args_dict 
from format_converters.ImportExportParamManager import fbx2objArgParser, ImportExportArgManager, ImportArgsManager
from scene_manager.scene_manager import set_empty_scene, set_animation_frame, get_start_animation_frame, \
    get_end_animation_frame, reset_blend

from exporters.meshExporter import ExportFramesAsMesh, export_texture_files
from importers.sceneImporter import ImportFbx

#def import_file(importArgsManager: ImportArgsManager):
#    conversion_function = get_conversion_function(ImportArgsManager.import_file_type)
import sys
import os
from typing import *
from inspect import signature
import argparse
import os


sys.path.append('.')
from utils.configure_paths import configure_paths
configure_paths()

from format_converters.converter import SceneFormatExporter, import_file, export_file, get_conversion_function, valid_formats, get_import_fn_args_dict,get_export_fn_args_dict
from format_converters.ImportExportParamManager import fbx2objArgParser, ImportExportArgManager, ImportArgsManager, ExportArgsManager
from scene_manager.scene_manager import set_empty_scene, set_animation_frame, get_start_animation_frame, get_end_animation_frame, get_keyframes_of_imported

class ArgumentParserForBlender(argparse.ArgumentParser):
    """
    This class is identical to its superclass, except for the parse_args
    method (see docstring). It resolves the ambiguity generated when calling
    Blender from the CLI with a python script, and both Blender and the script
    have arguments. E.g., the following call will make Blender crash because
    it will try to process the script's -a and -b flags:
    >>> blender --python my_script.py -a 1 -b 2

    To bypass this issue this class uses the fact that Blender will ignore all
    arguments given after a double-dash ('--'). The approach is that all
    arguments before '--' go to Blender, arguments after go to the script.
    The following calls work fine:
    >>> blender --python my_script.py -- -a 1 -b 2
    >>> blender --python my_script.py --
    """

    def _get_argv_after_doubledash(self):
        """
        Given the sys.argv as a list of strings, this method returns the
        sublist right after the '--' element (if present, otherwise returns
        an empty list).
        """
        try:
            idx = sys.argv.index("--")
            return sys.argv[idx+1:] # the list after '--'
        except ValueError as e: # '--' not in the list:
            return []

    # overrides superclass
    def parse_args(self):
        """
        This method is expected to behave identically as in the superclass,
        except that the sys.argv list will be pre-processed using
        _get_argv_after_doubledash before. See the docstring of the class for
        usage examples and details.
        """
        return super().parse_args(args=self._get_argv_after_doubledash())


def get_arg_parser():
    parser = ArgumentParserForBlender(description='Convert a folder of fbx to obj')

    parser.add_argument('-fbx_folder',  type=str,
                        help='The folder containing the fbx files to convert.')

    parser.add_argument('-obj_folder', type = str,
                        help = 'The folder containing the converted obj files.')

    #parser.add_argument('--frames', nargs = '+',
    #                    help = 'The frames to export.')
    return parser

def main():
    set_empty_scene()

    print("In main")
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    fbx_folder_loc = args.fbx_folder
    obj_folder_loc = args.obj_folder

    print("fbx_folder_loc: ", fbx_folder_loc)
    assert os.path.exists(fbx_folder_loc)
    assert os.path.exists(obj_folder_loc)
    fbx_files = os.listdir(fbx_folder_loc)

    importArgsManager = ImportArgsManager(import_file_type='fbx')
    exportArgsManager = ExportArgsManager(export_file_type="obj")

    exportArgsManagerGLFT = ExportArgsManager(export_file_type="gltf")

    for fbx_file in fbx_files:
        file_name, ext = os.path.splitext(fbx_file)
        if ext != ".fbx":
            print("skipping: ", fbx_file, " ext is " + ext + " and not fbx")
            continue

        obj_file_name = os.path.join(obj_folder_loc,file_name + ".obj")

        importArgsManager.set_import_arg("filepath", os.path.join(fbx_folder_loc, fbx_file))
        import_file(os.path.join(fbx_folder_loc, fbx_file), importArgsManager.get_import_args_dict(), verbose=True)

        end_frame = get_end_animation_frame()
        print("keys: ", get_keyframes_of_imported())
        print("Converting " + fbx_file + " to " + obj_file_name)

        exportArgsManager.set_export_arg("filepath", obj_file_name)
        exportArgsManager.set_export_arg("use_normals", True)
        exportArgsManager.set_export_arg("use_materials", True)
        exportArgsManager.set_export_arg("path_mode", "COPY")
        #exportArgsManager.set_export_arg("filter_glob", "*.obj;*.mtl;*.png")

        gltf_file_name = os.path.join(obj_folder_loc, file_name + ".gltf")
        exportArgsManagerGLFT.set_export_arg("export_format", "GLTF_SEPARATE")
        #exportArgsManagerGLFT.set_export_arg("export_image_format")
        exportArgsManagerGLFT.set_export_arg("filepath",  gltf_file_name)


        #exportArgsManager.set_export_arg("frame_end",end_frame)
        print("export {} to {} with args {}".format(fbx_file, obj_file_name, exportArgsManager.get_export_args_dict()))
        export_file(obj_file_name, kwargs=exportArgsManager.get_export_args_dict(), verbose=True)
        #export_file(gltf_file_name, kwargs=exportArgsManagerGLFT.get_export_args_dict(), verbose=True)

        set_empty_scene()
        reset_blend()


def fbx2obj():
    importArgsManager = ImportArgsManager(import_file_type='fbx')
    importArgsManager.set_import_arg("filepath", "data/test_input/fbx/Capoeira.fbx")
    import_file("data/test_input/fbx/Capoeira.fbx", importArgsManager.get_import_args_dict(), verbose=True)

    objExporter = ExportFramesAsMesh()
    objExporter.exportAnimationFramesAsMesh(r"data\test_output\obj\CapoeiraAnim", "capoeira", "obj", start_frame=1,
                                            end_frame=1, verbose=True)

    export_texture_files(r"data\test_output\obj\CapoeiraAnim")

if __name__ == '__main__':
    
    main()
    

    #converter.convertMesh(import_args["filepath"], export_args["filepath"], verbose = True)
    #objExporter.convertAnimationFrames(import_args["filepath"], export_args["filepath"], "aj", 1,100, verbose = True)
    
    
    
    
    
    
    
    
    
    
    
    