
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
from scene_manager.scene_manager import set_empty_scene, set_animation_frame
from format_converters.converter import import_file, export_file, convert
from example_scripts.format_conversion.fbx_to_gltf.fbx_to_gltf_all_frames import fbx_to_gltf
from format_converters.ImportExportParamManager import ImportArgsManager, ExportArgsManager


def get_arg_parser():
    parser = ArgumentParserForBlender(description='Convert a folder of fbx to gltf')

    parser.add_argument('-fbx_file', type=str,
                        help='The fbx file to convert.')

    parser.add_argument('-gltf_folder', type = str,
                        help = 'The folder containing the converted gltf files.')

    parser.add_argument("-frames", type = str, help = "The list of frames to export")
    return parser

def fbx_to_gltf_select_example(fbx_file_path, gltf_file_path):
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
    export_args_manager.set_export_arg("export_current_frame", True)

    return import_args_manager, export_args_manager


def main():
    separator = '#'
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()

    #export file name varies in loop, so initially set blank
    import_args_manager, export_args_manager = fbx_to_gltf_select_example(args.fbx_file, "")
    import_file(import_args_manager.get_import_args_dict())
    for frame_no in args.frames.split(' '):
        export_args_manager.set_export_arg("filepath", os.path.join(args.gltf_folder, os.path.basename(args.fbx_file + separator + "frame{:03d}.format(frame_no)" + ".bvh")))
        set_animation_frame(int(frame_no))
        export_file(export_args_manager.get_export_args_dict())



