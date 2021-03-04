import bpy
import mathutils
from math import radians

def CenterOrigin():
    #bpy.ops.transform.translate(value=(0, 0, 1), orient_type='GLOBAL')
    bpy.context.scene.cursor.location = mathutils.Vector((0.0, 0.0, 0.0))
    bpy.context.scene.cursor.rotation_euler = mathutils.Vector((0.0, 0.0, 0.0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    

def setRocketboxTPose():
    '''
    For a loaded rocketbox model, run this script to convert from A-Pose (default when downloaded) to T-Pose
    :return:
    '''
    CenterOrigin()

    bpy.ops.object.mode_set(mode = "POSE")
    context = bpy.context
    try:
        #for adults
        arm = bpy.data.objects["Bip01"]
    except KeyError:
        #for children
        arm = bpy.data.objects["Bip02"]

    bpy.ops.cats_manual.start_pose_mode()

    arm.pose.bones["Bip01 L Clavicle"].rotation_quaternion = mathutils.Quaternion((0.9961, 0.0881, -0.0039, 0.0050))
    arm.pose.bones["Bip01 L UpperArm"].rotation_quaternion = mathutils.Quaternion((0.9646, 0.1986, -0.0024, 0.1735))
    arm.pose.bones["Bip01 L Forearm"].rotation_quaternion = mathutils.Quaternion((0.9845, -0.0810, 0.0136, 0.1552))
    arm.pose.bones["Bip01 L Hand"].rotation_quaternion = mathutils.Quaternion((0.9898, 0.1132, 0.0502, -0.0710))
    arm.pose.bones["Bip01 L Finger0"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, 0.0000, 0.0000))
    arm.pose.bones["Bip01 L Finger01"].rotation_quaternion = mathutils.Quaternion((0.9992, 0.0030, 0.0189, 0.0346))
    arm.pose.bones["Bip01 L Finger02"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 L Finger1"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 L Finger11"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 L Finger12"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 L Finger2"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, -0.0000, 0.0000))
    arm.pose.bones["Bip01 L Finger21"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 L Finger22"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 L Finger3"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 L Finger31"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, 0.0000, 0.0000))
    arm.pose.bones["Bip01 L Finger32"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, 0.0000, 0.0000))
    arm.pose.bones["Bip01 L Finger4"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, 0.0000, 0.0000))
    arm.pose.bones["Bip01 L Finger41"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, -0.0000, -0.0000))
    arm.pose.bones["Bip01 L Finger42"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, -0.0000, 0.0000))

    arm.pose.bones["Bip01 R Clavicle"].rotation_quaternion = mathutils.Quaternion((0.9978, 0.0482, 0.0029, -0.0450))
    arm.pose.bones["Bip01 R UpperArm"].rotation_quaternion = mathutils.Quaternion((0.9508, 0.2309, -0.0023, -0.2065))
    arm.pose.bones["Bip01 R Forearm"].rotation_quaternion = mathutils.Quaternion((0.9799, 0.0084, -0.0204, -0.1981))
    arm.pose.bones["Bip01 R Hand"].rotation_quaternion = mathutils.Quaternion((0.9933, 0.0285, -0.0405, -0.1039))
    arm.pose.bones["Bip01 R Finger0"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, -0.0000, 0.0000))
    arm.pose.bones["Bip01 R Finger01"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, -0.0000, 0.0000))
    arm.pose.bones["Bip01 R Finger02"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, -0.0000, 0.0000))
    arm.pose.bones["Bip01 R Finger1"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 R Finger11"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, -0.0000, -0.0000))
    arm.pose.bones["Bip01 R Finger12"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, -0.0000, -0.0000))
    arm.pose.bones["Bip01 R Finger2"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 R Finger21"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, -0.0000, -0.0000))
    arm.pose.bones["Bip01 R Finger22"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 R Finger3"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 R Finger31"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, -0.0000, 0.0000))
    arm.pose.bones["Bip01 R Finger32"].rotation_quaternion = mathutils.Quaternion((1.0000, -0.0000, -0.0000, 0.0000))
    arm.pose.bones["Bip01 R Finger4"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 R Finger41"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, 0.0000, -0.0000))
    arm.pose.bones["Bip01 R Finger42"].rotation_quaternion = mathutils.Quaternion((1.0000, 0.0000, -0.0000, -0.0000))

    bpy.ops.cats_manual.pose_to_rest()

