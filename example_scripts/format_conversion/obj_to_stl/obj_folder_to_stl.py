import sys, os

#import user-defined modules after configure_paths()

try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

sys.path.append('.')
from utils.configure_paths import configure_paths
configure_paths()

from blender_arg_parser.blender_arg_parser import ArgumentParserForBlender
from utils.utils import apply_to_folder
from example_scripts.format_conversion.obj_to_stl.obj_to_stl import obj_to_stl_example
from format_converters.converter import convert_args_manager



def get_arg_parser():
    parser = ArgumentParserForBlender(description='Convert a folder of fbx to bvh')

    parser.add_argument('-obj_folder',  type=str,
                        help='The folder containing the fbx files to convert.')

    parser.add_argument('-recursive', type=bool,
                        help='Whether or not to search recursively for obj files to convert.')

    parser.add_argument('-stl_folder', type = str,
                        help = 'The folder containing the converted bvh files.')
    return parser



def main():
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    print("args", args)
    #converts each obj file to an stl file with 1-1 correspondence between file basename
    def convert_batch(obj_file, stl_file):
        convert_args_manager(*obj_to_stl_example(obj_file, stl_file, True), create_export_path=True)

    apply_to_folder(convert_batch, args.obj_folder, args.stl_folder, "stl", input_file_filter_function=lambda file_path: os.path.splitext(file_path)[1] == ".obj", recursive_search=args.recursive, verbose=True)

if __name__ == "__main__":
    main()