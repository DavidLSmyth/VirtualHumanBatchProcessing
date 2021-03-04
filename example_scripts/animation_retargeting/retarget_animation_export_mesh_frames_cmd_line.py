import argparse
import sys
import time
import random
import os

sys.path.append(".")
from animation_retargeting.animation_regargeting_api import retarget_and_export_animation, \
    retarget_animation_file_and_export_mesh_frames
from animation_retargeting.animation_retargeting_api_cmd_line import IndividualFramesAnimationRegargetingArgParser

def main():
    parser = IndividualFramesAnimationRegargetingArgParser()
    args = vars(parser.get_parser().parse_args())
    print("Read args: ", args)
    armature_files = args["armature_files"]
    animation_files = args["animation_files"]
    export_file_format = args["export_file_format"]
    frames_to_export = args["frames"]

    if len(armature_files) > 1:
        armature_files = armature_files.split(' ')
    if len(animation_files) > 1:
        animation_files = animation_files.split(' ')

    for animation_file, armature_file in zip(animation_files, armature_files):
        #retarget_animation_file_and_export_mesh_frames(import_armature_file_loc, import_animation_file_loc, export_extension, export_folder_location, frame_list = [], export_args_manager = None, animation_armature_name=None, mesh_armature_name=None):
        retarget_animation_file_and_export_mesh_frames(armature_file, animation_file, export_file_format, args["output_folder"], frames_to_export)



if __name__ == "__main__":
    main()