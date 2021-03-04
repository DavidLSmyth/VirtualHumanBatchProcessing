import os
import sys
import random
import argparse

sys.path.append(".")
from format_converters.converter import import_file, export_file
from scene_manager.scene_manager import set_animation_frame
from blender_arg_parser.blender_arg_parser import ArgumentParserForBlender
from example_scripts.format_conversion.fbx_to_obj.fbx_to_obj_all_frames import fbx_to_obj_example


try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)


def get_arg_parser():
    parser = ArgumentParserForBlender(description='Convert a folder of fbx to gltf')

    parser.add_argument('-fbx_file', type=str,
                        help='The fbx file to convert.')

    parser.add_argument('-obj_folder', type=str,
                        help='The folder containing the converted obj file.')

    parser.add_argument("-frames", type=str, nargs='+',
                        help="The frames to export")
    return parser


def export_obj_frames(import_args_manager, export_args_manager, args):
    separator = '#'
    import_file(import_args_manager.get_import_args_dict())

    for frame_no in args.frames:
        export_args_manager.set_export_arg("filepath", os.path.join(args.obj_folder, os.path.basename(
            args.fbx_file) + separator + "frame{:03d}".format(int(frame_no)) + ".obj"))
        set_animation_frame(int(frame_no))
        export_file(export_args_manager.get_export_args_dict())

def main():
    arg_parser = get_arg_parser()
    args = arg_parser.parse_args()

    import_args_manager, export_args_manager = fbx_to_obj_example(args.fbx_file, args.obj_folder, False)
    export_obj_frames(import_args_manager, export_args_manager, args)

if __name__ == "__main__":
    main()