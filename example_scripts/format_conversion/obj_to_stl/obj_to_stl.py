import sys


try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

sys.path.append('.')
from utils.configure_paths import configure_paths
configure_paths()

sys.path.append(".")
from blender_arg_parser.blender_arg_parser import ArgumentParserForBlender
from format_converters.converter import convert_args_manager
from format_converters.ImportExportParamManager import ImportArgsManager, ExportArgsManager
from scene_manager.scene_manager import reset_blend


def get_arg_parser():
    parser = ArgumentParserForBlender(description='Convert a folder of obj to gltf')

    parser.add_argument('-obj_file',  type=str,
                        help='The obj file to convert.')

    parser.add_argument('-stl_file', type = str,
                        help='The folder containing the converted stl file.')
    return parser


def obj_to_stl_example(obj_file_path, stl_file_path, use_anmiation = False):
    '''
    Use a function like this to set the import/export params
    :param obj_file_path: path to the obj file to import
    :param stl_file_path: path to the stl file to export
    :return:
    '''
    import_args_manager = ImportArgsManager(import_file_type='obj')
    export_args_manager = ExportArgsManager(export_file_type="stl")
    import_args_manager.set_import_arg("filepath", obj_file_path)

    export_args_manager.set_export_arg("filepath", stl_file_path)
    #save as ascii
    export_args_manager.set_export_arg("ascii", True)

    print(export_args_manager.get_export_args_dict())

    return import_args_manager, export_args_manager





def main():
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    reset_blend()
    convert_args_manager(*obj_to_stl_example(args.obj_file, args.stl_file, True))




if __name__ == "__main__":
    main()