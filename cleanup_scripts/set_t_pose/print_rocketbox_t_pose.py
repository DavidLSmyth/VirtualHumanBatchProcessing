'''
A script to print out the quaternion rotation of the skeleton.
Fix the pose one of your batch of skeletons (e.g. rocketbox) and then use this script to print rotations in a format that
can be directly pasted into another python file and ran to match the other skeletons in your batch with this pose.
Especially useful for tasks such as saving all rocketbox meshes in a T-Pose.
'''


import bpy
import mathutils
from math import radians

def print_rocketbox_T_pose():
    '''
    Use this to print the transformations needed to set rocketbox models to a T-pose
    :return:
    '''
    bpy.ops.object.mode_set(mode = "POSE")
    context = bpy.context
    arm = bpy.data.objects["Bip01"]


    l_clavicle_bone_name = "Bip01 L Clavicle" # change to suit
    l_clavicle_bone = arm.pose.bones[l_clavicle_bone_name]


    r_clavicle_bone_name = "Bip01 R Clavicle" # change to suit
    r_clavicle_bone = arm.pose.bones[r_clavicle_bone_name]


    print('arm.pose.bones["{}"].rotation_quaternion = mathutils.{}'.format(l_clavicle_bone.name, l_clavicle_bone.rotation_quaternion.__str__()))

    print('arm.pose.bones["{}"].rotation_quaternion = mathutils.{}'.format(r_clavicle_bone.name, r_clavicle_bone.rotation_quaternion.__str__()))

    def iterate(root):
        for child in root.children:
            print('arm.pose.bones["{}"].rotation_quaternion = mathutils.{}'.format(child.name, child.rotation_quaternion))
            iterate(child)

    iterate(l_clavicle_bone)
    iterate(r_clavicle_bone)

def main():
    print_T_pose()

if __name__ == "__main__":
    main()


