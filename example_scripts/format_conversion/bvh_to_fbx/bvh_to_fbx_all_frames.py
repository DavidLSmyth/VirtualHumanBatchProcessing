
import sys, os

try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

sys.path.append('.')
from utils.configure_paths import configure_paths
configure_paths()

from blender_arg_parser.blender_arg_parser import ArgumentParserForBlender
from format_converters.converter import  import_file, export_file
from format_converters.ImportExportParamManager import ImportArgsManager, ExportArgsManager
from scene_manager.scene_manager import set_empty_scene, get_start_animation_frame, get_end_animation_frame


def get_arg_parser():
    parser = ArgumentParserForBlender(description='Convert a bvh file to fbx format')

    parser.add_argument('-bvh_file',  type=str,
                        help='The bvh file to convert.')

    parser.add_argument('-fbx_file', type = str,
                        help = 'The location of the converted fbx file.')
    return parser

def bvh_to_fbx(bvh_file_path, fbx_file_path):
    import_args_manager = ImportArgsManager(import_file_type='bvh')
    export_args_manager = ExportArgsManager(export_file_type="fbx")

    import_args_manager.set_import_arg("filepath", bvh_file_path)
    import_file(import_args_manager.get_import_args_dict())

    export_args_manager.set_export_arg("filepath", fbx_file_path)


    export_file(kwargs=export_args_manager.get_export_args_dict(), verbose=True)
    set_empty_scene()


def main():
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    fbx_file_path = args.fbx_file
    bvh_file_path = args.bvh_file

    bvh_to_fbx(bvh_file_path, fbx_file_path)




if __name__ == "__main__":
    main()