import os

from example_scripts.RestPoseEditingScripts.setRocketboxTPoseCommandLine import saveRocketboxTPoseFBXMultiprocessed


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
    mesh_list = get_rocketbox_professions_A_pose_fbxs()
    output_dir = r"D:\SAUCEFiles\Microsoft-Rocketbox-master\Microsoft-Rocketbox-master\Assets\Avatars\Professions"
    saveRocketboxTPoseFBXMultiprocessed(mesh_list, output_dir)





if __name__ == "__main__":
    main()