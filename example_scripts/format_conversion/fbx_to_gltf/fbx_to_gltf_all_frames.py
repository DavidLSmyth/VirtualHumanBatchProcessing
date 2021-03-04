
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
from format_converters.converter import import_file, export_file, convert
from format_converters.ImportExportParamManager import ImportArgsManager, ExportArgsManager
from scene_manager.scene_manager import get_end_animation_frame, set_empty_scene


def get_arg_parser():
    parser = ArgumentParserForBlender(description='Convert a folder of fbx to gltf')

    parser.add_argument('-fbx_file',  type=str,
                        help='The fbx file to convert.')

    parser.add_argument('-gltf_file', type = str,
                        help='The folder containing the converted gltf file.')
    return parser


def fbx_to_gltf_all_frames_example(fbx_file_path, gltf_file_path):
    '''
    Use a function like this to set the import/export params
    :param fbx_file_path: path to the fbx file to import
    :param gltf_file_path: path to the gltf file to export
    :return:
    '''
    import_args_manager = ImportArgsManager(import_file_type='fbx')
    export_args_manager = ExportArgsManager(export_file_type="gltf")
    import_args_manager.set_import_arg("filepath", fbx_file_path)

    export_args_manager.set_export_arg("filepath", gltf_file_path)
    export_args_manager.set_export_arg("frame_end", get_end_animation_frame())

    return import_args_manager, export_args_manager


def fbx_to_gltf(import_args_manager, export_args_manager):
    import_file(import_args_manager.get_import_args_dict())
    export_file(kwargs=export_args_manager.get_export_args_dict(), verbose=True)
    set_empty_scene()


def main():
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    fbx_to_gltf(*fbx_to_gltf_all_frames_example(args.fbx_file, args.gltf_file))




if __name__ == "__main__":
    main()