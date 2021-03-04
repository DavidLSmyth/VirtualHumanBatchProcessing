
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
from scene_manager.scene_manager import set_empty_scene
from example_scripts.format_conversion.fbx_to_bvh.fbx_file_to_bvh_all_frames import fbx_to_bvh
from utils.utils import apply_to_folder

def get_arg_parser():
    parser = ArgumentParserForBlender(description='Convert a folder of fbx to bvh')

    parser.add_argument('-fbx_folder',  type=str,
                        help='The folder containing the fbx files to convert.')

    parser.add_argument('-bvh_folder', type = str,
                        help = 'The folder containing the converted bvh files.')
    return parser



def main():
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()
    apply_to_folder(args.fbx_folder, args.bvh_folder, "bvh", lambda file_path: os.path.splitext(file_path) == ".bvh")


if __name__ == "__main__":
    main()