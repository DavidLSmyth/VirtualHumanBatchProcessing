
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
    parser = ArgumentParserForBlender(description='Convert a fbx file to bvh format')

    parser.add_argument('-fbx_file',  type=str,
                        help='The fbx file to convert.')

    parser.add_argument('-bvh_file', type = str,
                        help = 'The location of the converted bvh file.')
    return parser

def fbx_to_bvh(fbx_file_path, bvh_file_path, all_frames = True):
    import_args_manager = ImportArgsManager(import_file_type='fbx')
    export_args_manager = ExportArgsManager(export_file_type="bvh")

    import_args_manager.set_import_arg("filepath", fbx_file_path)
    import_file(import_args_manager.get_import_args_dict())

    export_args_manager.set_export_arg("filepath", bvh_file_path)
    if all_frames:
        export_args_manager.set_export_arg("frame_end", get_end_animation_frame())
        export_args_manager.set_export_arg("frame_start", get_start_animation_frame())

    export_file(kwargs=export_args_manager.get_export_args_dict(), verbose=True)
    set_empty_scene()


def main():
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    fbx_file_path = args.fbx_file
    bvh_file_path = args.bvh_file

    fbx_to_bvh(fbx_file_path, bvh_file_path)




if __name__ == "__main__":
    main()