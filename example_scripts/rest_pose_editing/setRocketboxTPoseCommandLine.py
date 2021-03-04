import argparse
import sys
import time
import random
import os
import math

sys.path.append(".")
from example_scripts.RestPoseEditingScripts.setRocketboxTPose import saveRocketboxTPoseFBX

from Multiprocessing.multiprocess import run_multiprocessed

def get_cmd_line_args():
    argv = sys.argv
    print("argv before processing: ", argv)
    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"
    return argv


def get_arg_parser():
    usage_text = ('''Run me''')
    parser = argparse.ArgumentParser(description=usage_text)
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-rocketbox_folder_loc",
                           type=str)
    argparser.add_argument("-export_folder_loc",
                           type=str)
    return argparser



def saveRocketboxTPoseFBXMultiprocessed(rocketbox_fbx_list, destination_folder, no_cores = 8):
    #Initally wanted to send next files to render to stdin of each blender process but seems like there's a sync issue
    #
    #causes Error   : EXCEPTION_ACCESS_VIOLATION
    #Address : 0x00007FFA2682FB83
    #Module  : C:\Program Files\Blender Foundation\Blender 2.83\python37.dll

    active_cores = 0

    no_files_per_partition = math.ceil(len(rocketbox_fbx_list)/no_cores)
    no_partitions = no_cores
    mesh_partitions = [rocketbox_fbx_list[start*no_files_per_partition:start*no_files_per_partition+no_files_per_partition] for start in range(no_cores)]

    if input("using mesh_partitions: {}. Proceed?".format(mesh_partitions)) == 'n':
        sys.exit()

    #' '.join(next_to_retarget),
    #"-animation_armature_name", animation_armature_name, "-mesh_armature_name", mesh_armature_name] for next_to_retarget in mesh_partitions

    run_multiprocessed([["blender -b --python example_scripts\RestPoseEditingScripts\setRocketboxTPoseCommandLine.py -- -rocketbox_fbx_files {rocketbox_folder_loc} -export_folder_loc {export_folder_loc}".format(rocketbox_folder_loc = ' '.join(next_to_convert), export_folder_loc = destination_folder) for next_to_convert in mesh_partitions]])


def get_rocketbox_adult_A_pose_fbxs():
    mesh_dir = r"D:\SAUCEFiles\Microsoft-Rocketbox-master\Microsoft-Rocketbox-master\Assets\Avatars\Adults"
    mesh_names = os.listdir(mesh_dir)
    mesh_list = [os.path.join(mesh_dir, mesh_name, mesh_name + ".fbx") for mesh_name in mesh_names]
    return mesh_list

def get_rocketbox_child_A_pose_fbxs():
    mesh_dir = r"D:\SAUCEFiles\Microsoft-Rocketbox-master\Microsoft-Rocketbox-master\Assets\Avatars\Child"
    mesh_names = os.listdir(mesh_dir)
    mesh_list = [os.path.join(mesh_dir, mesh_name, mesh_name + ".fbx") for mesh_name in mesh_names]
    return mesh_list

def get_rocketbox_professions_A_pose_fbxs():
    mesh_dir = r"D:\SAUCEFiles\Microsoft-Rocketbox-master\Microsoft-Rocketbox-master\Assets\Avatars\Professions"
    mesh_names = os.listdir(mesh_dir)
    mesh_list = [os.path.join(mesh_dir, mesh_name, mesh_name + ".fbx") for mesh_name in mesh_names]
    return mesh_list

def get_rocketbox_adult_T_pose_fbxs():
    mesh_dir = r"D:\SAUCEFiles\Microsoft-Rocketbox-master\Microsoft-Rocketbox-master\Assets\Avatars\Adults"
    mesh_names = os.listdir(mesh_dir)
    mesh_list = [os.path.join(mesh_dir, mesh_name, mesh_name + "TPose.fbx") for mesh_name in mesh_names]
    return mesh_list

def get_rocketbox_child_T_pose_fbxs():
    mesh_dir = r"D:\SAUCEFiles\Microsoft-Rocketbox-master\Microsoft-Rocketbox-master\Assets\Avatars\Child"
    mesh_names = os.listdir(mesh_dir)
    mesh_list = [os.path.join(mesh_dir, mesh_name, mesh_name + "TPose.fbx") for mesh_name in mesh_names]
    return mesh_list

def get_rocketbox_professions_T_pose_fbxs():
    mesh_dir = r"D:\SAUCEFiles\Microsoft-Rocketbox-master\Microsoft-Rocketbox-master\Assets\Avatars\Professions"
    mesh_names = os.listdir(mesh_dir)
    mesh_list = [os.path.join(mesh_dir, mesh_name, mesh_name + "TPose.fbx") for mesh_name in mesh_names]
    return mesh_list


def main():
    argparser = get_arg_parser()

    print("running ")
    argv = get_cmd_line_args()
    print("argv: ", argv)
    args = vars(argparser.parse_known_args(argv)[0])
    print("read args: ", args)
    rocketbox_fbx_list = args["rocketbox_fbx_list"].split(' ')
    export_folder_loc = args["export_folder_loc"]
    # os.listdir(args["import_folder_loc"])

    #subfolders named according to model name
    #rocketbox_models = os.listdir(rocketbox_fbx_list)
    #a list of file paths to rocket fbx files
    #rocketbox_fbx_list = [os.path.join(rocketbox_folder, rocketbox_model, rocketbox_model + ".fbx") for rocketbox_model in rocketbox_models]

    for rocketbox_fbx in rocketbox_fbx_list:
        print("Retargeting to T_Pose ", rocketbox_fbx)
        print("saveRocketboxTPoseFBX(",rocketbox_fbx, export_folder_loc, os.path.splitext(os.path.basename(rocketbox_fbx))[0] + "TPose.fbx")
        saveRocketboxTPoseFBX(rocketbox_fbx, os.path.join(export_folder_loc, os.path.splitext(os.path.basename(rocketbox_fbx))[0]), os.path.splitext(os.path.basename(rocketbox_fbx))[0] + "TPose.fbx")


# time.sleep(random.random() * 2)
# argparser.parse_args([next_line])


if __name__ == "__main__":
    main()