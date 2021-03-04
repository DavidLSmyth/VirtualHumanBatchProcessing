
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
from format_converters.converter import convert_args_manager
from format_converters.ImportExportParamManager import ImportArgsManager, ExportArgsManager


def get_arg_parser():
    parser = ArgumentParserForBlender(description='Convert a folder of fbx to gltf')

    parser.add_argument('-fbx_file',  type=str,
                        help='The fbx file to convert.')

    parser.add_argument('-obj_file', type = str,
                        help='The folder containing the converted obj file.')
    return parser


def fbx_to_obj_example(fbx_file_path, obj_file_path, use_anmiation = False):
    '''
    Use a function like this to set the import/export params
    :param fbx_file_path: path to the fbx file to import
    :param obj_file_path: path to the obj file to export
    :return:
    '''
    import_args_manager = ImportArgsManager(import_file_type='fbx')
    export_args_manager = ExportArgsManager(export_file_type="obj")
    import_args_manager.set_import_arg("filepath", fbx_file_path)

    export_args_manager.set_export_arg("filepath", obj_file_path)
    export_args_manager.set_export_arg("use_animation", use_anmiation)

    return import_args_manager, export_args_manager





def main():
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    convert_args_manager(*fbx_to_obj_example(args.fbx_file, args.obj_file, True))




if __name__ == "__main__":
    main()