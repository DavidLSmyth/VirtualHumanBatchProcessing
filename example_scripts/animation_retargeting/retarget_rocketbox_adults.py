
import math
import sys
import os
import time
from pathlib import Path
sys.path.append(".")
from Multiprocessing.multiprocess import run_multiprocessed


def test():
    print("Running multiprocessed")
    run_multiprocessed([["python", "-m", "pip", "list"], ["ipconfig"]])

def retarget_multiprocessed(mesh_file_list, animation_file_loc, export_folder_loc ,animation_armature_name, mesh_armature_name, frame_no = None, no_cores = 4):
    #Initally wanted to send next files to render to stdin of each blender process but seems like there's a sync issue
    #
    #causes Error   : EXCEPTION_ACCESS_VIOLATION
    #Address : 0x00007FFA2682FB83
    #Module  : C:\Program Files\Blender Foundation\Blender 2.83\python37.dll

    no_files_per_partition = math.ceil(len(mesh_file_list)/no_cores)
    mesh_partitions = [mesh_file_list[start*no_files_per_partition:start*no_files_per_partition+no_files_per_partition] for start in range(no_cores)]

    run_multiprocessed([["blender", "-b", "--python",
                         r"example_scripts\retargeting_examples\rocketbox_with_mixamo\retarget_multiple_frame_cmd_line.py",
                         "--", "-export_folder_loc", export_folder_loc, "-animation_file", animation_file_loc, "-frame_no", "-1", "-import_files", ' '.join(next_to_retarget),
                         "-animation_armature_name", animation_armature_name, "-mesh_armature_name", mesh_armature_name] for next_to_retarget in mesh_partitions])


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

def get_animation_names(animations_folder):
    #r"C:\Users\admin\Documents\3dGeom\SquatData\SquatAnimations"
    animation_files = os.listdir(animations_folder)
    animations_names = list(map(lambda x: Path(x).stem, animation_files))
    return animations_names

def main():
    #mesh_dir = r"D:\SAUCEFiles\Microsoft-Rocketbox-master\testTPose"
    #mesh_names = os.listdir(mesh_dir)
    #mesh_list_adults = get_rocketbox_adult_T_pose_fbxs()
    #mesh_list_professions = get_rocketbox_professions_T_pose_fbxs()
    animations_folder = r"C:\Users\admin\Documents\3dGeom\SquatData\SquatAnimations"
    output_fbx_folder = r"C:\Users\admin\Documents\3dGeom\SquatData\SquatFBXMeshes"
    animation_names = get_animation_names(animations_folder)

    #have been manually changing some of these to make sure that each is ok before running the next.
    for string in ["Adults"]:
        #animation for Susana's Pifu stuff
        #for animation in ["angry"]:#, "defeated"]:#, "old_man_idle", "reaction", "hip_hop_dancing", "silly_dancing", "rumba_dancing", "standing_torch_light_torch", "using_a_fax_machine", "bboy_uprock_start", "dodging_right"]:
        for animation in [animation_names[7]]:
            #retarget_multiprocessed(mesh_file_list, animation_file_loc, export_folder_loc ,animation_armature_name, mesh_armature_name, frame_no = None, no_cores = 8)

            #usually best to run on maximum 4 processes, otherwise cpu struggles
            #in future write semaphore to a file to indicate each subprocess is done, then start another
            retarget_multiprocessed(get_rocketbox_adult_T_pose_fbxs() if string == "Adults" else get_rocketbox_professions_T_pose_fbxs(), animations_folder + "\{}.fbx".format(animation), output_fbx_folder + "{}\{}".format(string, animation), "Armature", "Bip01", no_cores = 4)

if __name__ == '__main__':
    main()