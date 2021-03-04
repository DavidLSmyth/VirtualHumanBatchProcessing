
import math
import sys
import os
sys.path.append(".")
from Multiprocessing.multiprocess import run_multiprocessed



def retarget_multiprocessed(mesh_file_list, animation_file_loc, export_folder_loc ,animation_armature_name, mesh_armature_name,  no_cores = 4):
    '''
    For a list of mesh/armature files, retarget an animation and export
    :param mesh_file_list:
    :param animation_file_loc:
    :param export_folder_loc:
    :param animation_armature_name:
    :param mesh_armature_name:
    :param no_cores:
    :return:
    '''
    #Initally wanted to send next files to render to stdin of each blender process but seems like there's a sync issue
    #
    #causes Error   : EXCEPTION_ACCESS_VIOLATION
    #Address : 0x00007FFA2682FB83
    #Module  : C:\Program Files\Blender Foundation\Blender 2.83\python37.dll

    active_cores = 0

    no_files_per_partition = math.ceil(len(mesh_file_list)/no_cores)
    no_partitions = no_cores
    mesh_partitions = [mesh_file_list[start*no_files_per_partition:start*no_files_per_partition+no_files_per_partition] for start in range(no_cores)]

    if input("using mesh_partitions: {}. Proceed?".format(mesh_partitions)) == 'n':
        sys.exit()


    run_multiprocessed([["blender", "-b", "--python",
                         r"D:\TCDFiles\3dGeom\AnimationRetargeting\blender3dgscripts\example_scripts\retargeting_examples\rocketbox_with_mixamo\retarget_multiple_frame_cmd_line.py",
                         "--", "-export_folder_loc", export_folder_loc, "-animation_file", animation_file_loc, "-start_frame", "1", "-end_frame", "57", "-import_files", ' '.join(next_to_retarget),
                         "-animation_armature_name", animation_armature_name, "-mesh_armature_name", mesh_armature_name] for next_to_retarget in mesh_partitions])

#    while active_cores < no_cores:
#        next_to_retarget = mesh_partitions.pop()
#        subprocess.Popen( )
#        active_cores += 1
    print("opened all windows")

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


    mesh_dir = r"D:\SAUCEFiles\Microsoft-Rocketbox-master\Microsoft-Rocketbox-master\Assets\Avatars\Children"
    mesh_names = os.listdir(mesh_dir)
    mesh_list = get_rocketbox_adult_T_pose_fbxs()


    print("mesh_list: ", mesh_list)
    retarget_multiprocessed(mesh_list, r"D:\TCDFiles\3dGeom\SquatData\Animation\FBX\air_squat.fbx", r"D:\TCDFiles\3dGeom\SquatData\SquatMeshes", "Armature", "Bip02", no_cores = 4)


if __name__ == '__main__':
    main()