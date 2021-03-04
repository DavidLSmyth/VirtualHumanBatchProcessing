import math

import sys
import os
import sys
import random

sys.path.append(".")
from format_converters import get_import_fn_args_dict, import_file, get_export_fn_args_dict, export_file
from scene_manager.scene_manager import reset_blend, deselect_all, get_start_animation_frame, get_end_animation_frame
from animation_retargeting.API.retargeting import retarget_main

try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

from Multiprocessing.multiprocess import run_multiprocessed
from cleanup_scripts.SetTPose.setTPose import setRocketboxTPose

def test():
    print("Running multiprocessed")
    run_multiprocessed([["python", "-m", "pip", "list"], ["ipconfig"]])

def saveRocketboxTPoseFBX(rocketboxFBX, destination_folder, destination_file_name):
    '''
    :param rocketboxFBX: Location of a rocketbox fbfx file
    :param destination_folder: Folder to save the fbx with T-Pose.
    :param destination_file_name: The file name to save to
    :return:
    '''
    reset_blend()

    # load mesh & armature
    import_file_loc = rocketboxFBX  # r"D:\TCDFiles\3dGeom\SquatData\Mesh\Female_Adult_01\Female_Adult_01.fbx"
    import_args = get_import_fn_args_dict("fbx")

    import_args["filepath"] = import_file_loc
    import_args["use_anim"] = False
    import_args["force_connect_children"] = True

    import_file(import_file_loc, import_args, verbose=True)

    # retarget animation from source armature to target armature
    setRocketboxTPose()



    export_file_loc = os.path.join(destination_folder, destination_file_name)  # r"D:\TCDFiles\3dGeom\SquatData\SquatMeshes\Female_Adult_01#air_squat.fbx"
    print("exporting to " + export_file_loc)
    export_args = get_export_fn_args_dict("fbx")
    export_args["filepath"] = export_file_loc

    # export_args["use_selection"] = True
    export_args["embed_textures"] = True
    #export_args["bake_anim"] = start_frame != end_frame
    print(export_args)
    export_file(export_file_loc, export_args, verbose=True)






if __name__ == "__main__":
    main()
