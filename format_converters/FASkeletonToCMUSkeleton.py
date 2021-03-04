import sys
import bpy
import re
import os
try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

sys.path.append('.')

from utils.configure_paths import configure_paths
from scene_manager.scene_manager import set_empty_scene
configure_paths()

from scene_manager.scene_manager import set_empty_scene
from format_converters.converter import  get_export_fn_args_dict, get_import_fn_args_dict, import_file, export_file


def retarget_FA_to_CMU(fa_file, cmu_file, output_bvh_file_loc):
    assert fa_file[-3:] == 'bvh'
    assert cmu_file[-3:] == 'bvh'

    set_empty_scene(True)
    cmu_import_file_name = re.findall(".*/([0-9]{0,3}_[0-9]{0,3}).bvh", cmu_file)[0]

    import_args = get_import_fn_args_dict("bvh")

    import_args["filepath"] = cmu_file

    import_file(cmu_file, import_args, verbose=True)

    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.pose.armature_apply(selected=False)

    fa_import_file_name = re.findall(".*/(loc_0[0-9]{0,3}).bvh", fa_file)[0]

    import_file_loc = fa_file
    import_args["filepath"] = import_file_loc
    import_file(import_file_loc, import_args, verbose=True)

    # rescale so source matches target
    bpy.context.selected_objects[0].scale[0] = 0.2
    bpy.context.selected_objects[0].scale[1] = 0.2
    bpy.context.selected_objects[0].scale[2] = 0.2

    # bpy.data.objects['Cube'].select_set(True)

    # bpy.data.objects[fa_import_file_name].select_set(True)
    bpy.data.scenes["Scene"].rsl_retargeting_armature_source = bpy.data.objects[fa_import_file_name]
    bpy.data.scenes["Scene"].rsl_retargeting_armature_target = bpy.data.objects[cmu_import_file_name]

    print("available ops: ", dir(bpy.ops.rsl.import_custom_schemes))

    # load_custom_lists_from_file(r"C:/users/admin/Downloads/FAToCMU.json")
    # bpy.ops.rsl.import_custom_schemes.directory = r"C:/users/admin/Downloads/"
    # files = bpy.types.OperatorFileListElement('INVOKE_DEFAULT')
    # bpy.ops.rsl.import_custom_schemes( directory = r"C:/users/admin/Downloads/FAToCMU.json")
    bpy.ops.rsl.build_bone_list()
    bpy.ops.rsl.retarget_animation()

    bpy.data.objects[cmu_import_file_name].select_set(True)

    export_temp = r"./temp.bvh"
    export_args = get_export_fn_args_dict("bvh")
    export_args["filepath"] = export_temp
    export_args["root_transform_only"] = True
    export_file(export_temp, export_args)

    set_empty_scene(True)

    # re-import file with correct orientations
    import_args["filepath"] = export_temp
    import_args["axis_forward"] = "Z"
    import_args["axis_up"] = "X"
    import_file(export_temp, import_args)

    export_args["rotate_mode"] = "ZYX"
    export_args["filepath"] = output_bvh_file_loc
    export_file(output_bvh_file_loc, export_args)

    os.remove(export_temp)




if __name__ == "__main__":
    #if the name of the json file changes, update <>
   #retarget_FA_to_CMU("D:/SAUCEFiles/MotionDatabase/Database/BVH/loc_0006.bvh",r"D:/SAUCEFiles/MotionDatabase/Database/BVH/120_10.bvh", r"C:/Users/admin/Documents/test.bvh" )
    retarget_FA_to_CMU("C:/users/admin/Downloads/loc_001.bvh",r"D:/SAUCEFiles/MotionDatabase/Database/BVH/120_10.bvh", r"C:/users/admin/Downloads/afpum_001_retargeted.bvh")
