import bpy
import copy

import os
import json
import pathlib

import sys
print(sys.path.append("."))
from animation_retargeting.API import utils

from animation_retargeting.API.bones import bone_list, ignore_rokoko_retargeting_bones
from animation_retargeting.API.shapes import shape_list
from format_converters.converter import  *
from scene_manager.scene_manager import deselect_all, reset_blend

RETARGET_ID = '_RSL_RETARGET'

bone_detection_list = {}
bone_detection_list_unmodified = {}
bone_detection_list_custom = {}
shape_detection_list = {}
shape_detection_list_unmodified = {}
shape_detection_list_custom = {}

main_dir = str(pathlib.Path(os.path.dirname(__file__)).parent.resolve())
resources_dir = os.path.join(main_dir, "resources")
custom_bones_dir = os.path.join(resources_dir, "custom_bones")
custom_bone_list_file = os.path.join(custom_bones_dir, "custom_bone_list.json")




class RetargetAnimation:
    #bl_idname = "rsl.retarget_animation"
    #bl_label = "Retarget Animation"
    #bl_description = "Retargets the animation from the source armature to the target armature"
    #bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, armature_source, armature_target, auto_scaling: "bool", retargeting_bone_list ):
        #armature_source = get_source_armature()
        #armature_target = get_target_armature()

        if not armature_source.animation_data or not armature_source.animation_data.action:
            raise Exception("No animation attached to {}".format(armature_source.name))
        #    self.report({'ERROR'}, 'No animation on the source armature found!'
        #]                           '\nSelect an armature with an animation as source.')
        #    return {'CANCELLED'}

        if armature_source.name == armature_target.name:
            self.report({'ERROR'}, 'Source and target armature are the same!'
                                   '\nPlease select different armatures.')
            return {'CANCELLED'}

        # Find root bones
        root_bones = self.find_root_bones(retargeting_bone_list, armature_source, armature_target)

        # Cancel if no root bones are found
        if not root_bones:
            self.report({'ERROR'}, 'No root bone found!'
                                   '\nCheck if the bones are mapped correctly or try rebuilding the bone list.')
            return {'CANCELLED'}

        # Save the bone list if the user changed anything
        save_retargeting_to_list(armature_source, armature_target)

        # Prepare armatures
        utils.set_active(armature_target)
        bpy.ops.object.mode_set(mode='OBJECT')
        utils.set_active(armature_source)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Set armatures into pose mode
        armature_source.data.pose_position = 'POSE'
        armature_target.data.pose_position = 'POSE'

        # Save and reset the current pose position of both armatures if rest position should be used
        pose_source, pose_target = {}, {}
        if bpy.context.scene.rsl_retargeting_use_pose == 'REST':
            pose_source = self.get_and_reset_pose_rotations(armature_source)
            pose_target = self.get_and_reset_pose_rotations(armature_target)

        source_scale = None
        if auto_scaling:
            # Clean source animation
            self.clean_animation(armature_source)

            # Scale the source armature to fit the target armature
            source_scale = copy.deepcopy(armature_source.scale)
            self.scale_armature(retargeting_bone_list, armature_source, armature_target, root_bones)

        # Duplicate source armature to apply transforms to the animation
        armature_source_original = armature_source
        armature_source = self.copy_rest_pose(armature_source)

        # Save transforms of target armature
        rotation_mode = armature_target.rotation_mode
        armature_target.rotation_mode = 'QUATERNION'
        rotation = copy.deepcopy(armature_target.rotation_quaternion)
        location = copy.deepcopy(armature_target.location)

        # Apply transforms of the target armature
        bpy.ops.object.select_all(action='DESELECT')
        utils.set_active(armature_target)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        bpy.ops.object.mode_set(mode='EDIT')

        # Create a transformation dict of all bones of the target armature and unselect all bones
        bone_transforms = {}
        for bone in bpy.context.object.data.edit_bones:
            bone.select = False
            bone_transforms[bone.name] = armature_source.matrix_world.inverted() @ bone.head.copy(), \
                                         armature_source.matrix_world.inverted() @ bone.tail.copy(), \
                                         utils.mat3_to_vec_roll(armature_source.matrix_world.inverted().to_3x3() @ bone.matrix.to_3x3())  # Head loc, tail loc, bone roll

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        utils.set_active(armature_source)
        bpy.ops.object.mode_set(mode='EDIT')

        # Recreate bones from target armature in source armature
        for item in retargeting_bone_list:
            if not item.bone_name_source or not item.bone_name_target or item.bone_name_target not in bone_transforms:
                continue

            bone_source = armature_source.data.edit_bones.get(item.bone_name_source)
            if not bone_source:
                print('Skipped:', item.bone_name_source, item.bone_name_target)
                continue

            # Recreate target bone
            bone_new = armature_source.data.edit_bones.new(item.bone_name_target + RETARGET_ID)
            bone_new.head, bone_new.tail, bone_new.roll = bone_transforms[item.bone_name_target]
            bone_new.parent = bone_source

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # Add constraints to target armature and select the bones for animation
        for item in retargeting_bone_list:
            if not item.bone_name_source or not item.bone_name_target:
                continue

            bone_source = armature_source.pose.bones.get(item.bone_name_source)
            bone_target = armature_target.pose.bones.get(item.bone_name_target)
            bone_target_data = armature_target.data.bones.get(item.bone_name_target)

            if not bone_source or not bone_target or not bone_target_data:
                print('Bone mapping not found:', item.bone_name_source, item.bone_name_target)
                continue

            # Add constraints
            constraint = bone_target.constraints.new('COPY_ROTATION')
            constraint.name += RETARGET_ID
            constraint.target = armature_source
            constraint.subtarget = item.bone_name_target + RETARGET_ID

            if bone_target.name in root_bones:
                constraint = bone_target.constraints.new('COPY_LOCATION')
                constraint.name += RETARGET_ID
                constraint.target = armature_source
                constraint.subtarget = item.bone_name_source

            # Select the bone for animation
            armature_target.data.bones.get(item.bone_name_target).select = True

        # Bake the animation to the target armature
        self.bake_animation(armature_source, armature_target, root_bones)

        # Delete the duplicate helper armature
        bpy.ops.object.select_all(action='DESELECT')
        utils.set_active(armature_source)
        bpy.data.actions.remove(armature_source.animation_data.action)
        bpy.ops.object.delete()

        # Change armature source back to original
        armature_source = armature_source_original

        # Change action name
        armature_target.animation_data.action.name = armature_source.animation_data.action.name + ' Retarget'

        # Remove constraints from target armature
        for bone in armature_target.pose.bones:
            for constraint in bone.constraints:
                if RETARGET_ID in constraint.name:
                    bone.constraints.remove(constraint)

        bpy.ops.object.select_all(action='DESELECT')
        utils.set_active(armature_target)

        # Reset target armature transforms to old state
        armature_target.rotation_quaternion = rotation
        armature_target.location = location

        armature_target.rotation_quaternion.w = -armature_target.rotation_quaternion.w
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        armature_target.rotation_quaternion = rotation
        armature_target.rotation_mode = rotation_mode

        # Reset source armature scale
        if source_scale:
            armature_source.scale = source_scale

        # Reset pose positions to old state
        # self.load_pose_rotations(armature_source, pose_source)
        # self.load_pose_rotations(armature_target, pose_target)

        bpy.ops.object.select_all(action='DESELECT')

        #self.report({'INFO'}, 'Retargeted animation.')
        print("Retargeted animation")
        print("finished")
        #return {'FINISHED'}

    def find_root_bones(self, retargeting_bone_list, armature_source, armature_target):
        # Find all root bones
        root_bones = []
        for bone in armature_target.pose.bones:
            if not bone.parent:
                root_bones.append(bone)

        # Find animated root bones
        root_bones_animated = []
        print([item for item in retargeting_bone_list])
        target_bones = [item.bone_name_target for item in retargeting_bone_list if
                        armature_target.pose.bones.get(item.bone_name_target) and armature_source.pose.bones.get(item.bone_name_source)]
        while root_bones:
            for bone in copy.copy(root_bones):
                root_bones.remove(bone)
                if bone.name in target_bones:
                    root_bones_animated.append(bone.name)
                else:
                    for bone_child in bone.children:
                        root_bones.append(bone_child)
        return root_bones_animated

    def clean_animation(self, armature_source):
        deletable_fcurves = ['location', 'rotation_euler', 'rotation_quaternion', 'scale']
        for fcurve in armature_source.animation_data.action.fcurves:
            if fcurve.data_path in deletable_fcurves:
                armature_source.animation_data.action.fcurves.remove(fcurve)

    def get_and_reset_pose_rotations(self, armature):
        bpy.ops.object.select_all(action='DESELECT')
        utils.set_active(armature)
        bpy.ops.object.mode_set(mode='POSE')

        # Save rotations
        pose_rotations = {}
        for bone in armature.pose.bones:
            if bone.rotation_mode == 'QUATERNION':
                pose_rotations[bone.name] = copy.deepcopy(bone.rotation_quaternion)
                bone.rotation_quaternion = (1, 0, 0, 0)
            else:
                pose_rotations[bone.name] = copy.deepcopy(bone.rotation_euler)
                bone.rotation_euler = (0, 0, 0)

        # Reset rotations
        # bpy.ops.pose.rot_clear()
        bpy.ops.object.mode_set(mode='OBJECT')

        return pose_rotations

    def load_pose_rotations(self, armature, pose_rotations):
        if not pose_rotations:
            return

        bpy.ops.object.select_all(action='DESELECT')
        utils.set_active(armature)
        bpy.ops.object.mode_set(mode='POSE')

        # Load rotations
        for bone in armature.pose.bones:
            rot = pose_rotations.get(bone.name)
            if rot:
                if bone.rotation_mode == 'QUATERNION':
                    bone.rotation_quaternion = rot
                else:
                    bone.rotation_euler = rot

        bpy.ops.object.mode_set(mode='OBJECT')

    def scale_armature(self, retargeting_bone_list, armature_source, armature_target, root_bones):
        source_min = None
        source_min_root = None
        target_min = None
        target_min_root = None

        for item in retargeting_bone_list:
            if not item.bone_name_source or not item.bone_name_target:
                continue

            bone_source = armature_source.pose.bones.get(item.bone_name_source)
            bone_target = armature_target.pose.bones.get(item.bone_name_target)
            if not bone_source or not bone_target:
                continue

            bone_source_z = (armature_source.matrix_world @ bone_source.head)[2]
            bone_target_z = (armature_target.matrix_world @ bone_target.head)[2]

            if item.bone_name_target in root_bones:
                if source_min_root is None or source_min_root > bone_source_z:
                    source_min_root = bone_source_z
                if target_min_root is None or target_min_root > bone_target_z:
                    target_min_root = bone_target_z

            if source_min is None or source_min > bone_source_z:
                source_min = bone_source_z
            if target_min is None or target_min > bone_target_z:
                target_min = bone_target_z

        source_height = source_min_root - source_min
        target_height = target_min_root - target_min

        if not source_height or not target_height:
            print('No scaling needed')
            return

        scale_factor = target_height / source_height
        armature_source.scale *= scale_factor

    def read_anim_start_end(self, armature):
        frame_start = None
        frame_end = None
        for fcurve in armature.animation_data.action.fcurves:
            for key in fcurve.keyframe_points:
                keyframe = key.co.x
                if frame_start is None:
                    frame_start = keyframe
                if frame_end is None:
                    frame_end = keyframe

                if keyframe < frame_start:
                    frame_start = keyframe
                if keyframe > frame_end:
                    frame_end = keyframe

        return frame_start, frame_end

    def copy_rest_pose(self,  armature_source):
        # make sure auto keyframe is disabled, leads to issues
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = False

        # ensure the source armature selection
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        utils.set_active(armature_source)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Duplicate the source armature
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'},
                                      TRANSFORM_OT_translate={"value": (0, 0, 0), "constraint_axis": (False, True, False), "mirror": False, "snap": False, "remove_on_cancel": False,
                                                              "release_confirm": False})

        # Set name of the copied source armature
        source_armature_copy = bpy.context.object
        source_armature_copy.name = armature_source.name + "_copy"

        bpy.ops.object.select_all(action='DESELECT')
        utils.set_active(source_armature_copy)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='POSE')

        # Apply transforms of the new source armature. Unlink action temporarily to prevent warning in console
        action_tmp = source_armature_copy.animation_data.action
        source_armature_copy.animation_data.action = None
        bpy.ops.pose.armature_apply()
        source_armature_copy.animation_data.action = action_tmp

        # Mimic the animation of the original source armature by adding constraints to the bones.
        # -> the new armature has the exact same animation but with applied transforms
        for bone in source_armature_copy.pose.bones:
            constraint = bone.constraints.new('COPY_TRANSFORMS')
            constraint.name = bone.name
            constraint.target = armature_source
            constraint.subtarget = bone.name

        bpy.ops.object.mode_set(mode='OBJECT')

        return source_armature_copy

    def bake_animation(self, armature_source, armature_target, root_bones):
        frame_split = 25
        frame_start, frame_end = self.read_anim_start_end(armature_source)
        frame_start, frame_end = int(frame_start), int(frame_end)
        utils.set_active(armature_target)

        actions_all = []

        # Setup loading bar
        current_step = 0
        steps = int((frame_end - frame_start) / frame_split) + 1
        wm = bpy.context.window_manager
        wm.progress_begin(current_step, steps)

        import time
        start_time = time.time()

        # Bake the animation in parts because multiple short parts are processed much faster than one long animation
        for frame in range(frame_start, frame_end + 2, frame_split):
            start = frame
            end = frame + frame_split - 1
            if end > frame_end:
                end = frame_end
            if start > end:
                continue

            # Bake animation part
            bpy.ops.nla.bake(frame_start=start, frame_end=end, visual_keying=True, only_selected=True, use_current_action=False, bake_types={'POSE'})

            # Rename animation part
            armature_target.animation_data.action.name = 'RSL_RETARGETING_' + str(frame)

            actions_all.append(armature_target.animation_data.action)

            current_step += 1
            if steps != current_step:
                wm.progress_update(current_step)

        if not actions_all:
            return

        # Count all keys for all data_paths
        key_counts = {}
        for action in actions_all:
            for fcurve in action.fcurves:
                key = fcurve.data_path + str(fcurve.array_index)
                if not key_counts.get(key):
                    key_counts[key] = 0
                key_counts[key] += len(fcurve.keyframe_points)

        # Create new action
        action_final = bpy.data.actions.new(name='RSL_RETARGETING_FINAL')
        action_final.use_fake_user = True
        armature_target.animation_data_create().action = action_final

        # Put all baked animations parts back together into one
        print_i = 0
        for fcurve in actions_all[0].fcurves:
            if fcurve.data_path.endswith('scale'):
                continue
            if fcurve.data_path.endswith('location'):
                bone_name = fcurve.data_path.split('"')
                if len(bone_name) != 3:
                    continue
                if bone_name[1] not in root_bones:
                    continue

            curve_final = action_final.fcurves.new(data_path=fcurve.data_path, index=fcurve.array_index, action_group=fcurve.group.name)
            keyframe_points = curve_final.keyframe_points
            keyframe_points.add(key_counts[fcurve.data_path + str(fcurve.array_index)])

            index = 0
            for action in actions_all:
                fcruve_to_add = action.fcurves.find(data_path=fcurve.data_path, index=fcurve.array_index)

                for kp in fcruve_to_add.keyframe_points:
                    keyframe_points[index].co.x = kp.co.x
                    keyframe_points[index].co.y = kp.co.y
                    keyframe_points[index].interpolation = 'LINEAR'
                    index += 1

            print_i += 1

        # Clean up animation. Delete all keyframes the use the same value as the previous and next one
        for fcurve in action_final.fcurves:
            if len(fcurve.keyframe_points) <= 2:
                continue

            kp_pre_pre = fcurve.keyframe_points[0]
            kp_pre = fcurve.keyframe_points[1]

            kp_to_delete = []
            for kp in fcurve.keyframe_points[2:]:
                if round(kp_pre_pre.co.y, 5) == round(kp_pre.co.y, 5) == round(kp.co.y, 5):
                    kp_to_delete.append(kp_pre)
                kp_pre_pre = kp_pre
                kp_pre = kp

            for kp in reversed(kp_to_delete):
                fcurve.keyframe_points.remove(kp)

        # Delete all baked animation parts, only the combined one is needed
        for action in actions_all:
            bpy.data.actions.remove(action)

        print('Retargeting Time:', round(time.time() - start_time, 2), 'seconds')
        wm.progress_end()




def save_retargeting_to_list(armature_source, armature_target):
    global bone_detection_list, bone_detection_list_custom
    armature_target# = retargeting.get_target_armature()
    retargeting_dict = detect_retarget_bones(armature_source, armature_target)

    for bone_item in bpy.context.scene.rsl_retargeting_bone_list:
        if not bone_item.bone_name_source or not bone_item.bone_name_target:
            continue

        bone_name_key = bone_item.bone_name_key
        bone_name_source = bone_item.bone_name_source.lower()
        bone_name_target = bone_item.bone_name_target.lower()
        bone_name_target_detected, bone_name_key_detected = retargeting_dict[bone_item.bone_name_source]

        if bone_name_target_detected == bone_item.bone_name_target:
            continue

        if bone_name_key_detected and bone_name_key_detected != 'spine':
            if not bone_detection_list_custom.get(bone_name_key_detected):
                bone_detection_list_custom[bone_name_key_detected] = []

            # TODO Idea: If a target bone got detected but was removed and left empty, add it to an ignore list. So if that exact match-up gets detected again, leave it empty

            # If the detected target is in the custom bones list but it got changed, remove it from the list. If the new bone gets detected automatically now, don't add it to the custom list
            if bone_name_target_detected.lower() in bone_detection_list_custom[bone_name_key_detected]:
                if bone_name_key_detected.startswith('custom_bone_') and len(bone_detection_list_custom[bone_name_key_detected]) == 2:
                    bone_detection_list_custom.pop(bone_name_key_detected)
                else:
                    bone_detection_list_custom[bone_name_key_detected].remove(bone_name_target_detected.lower())

                # Update the bone detection list in order to correctly figure out if the new selected bone needs to be saved
                bone_detection_list = combine_lists(bone_detection_list_unmodified, bone_detection_list_custom)

                retargeting_dict = detect_retarget_bones()
                bone_name_detected_new, _ = retargeting_dict[bone_item.bone_name_source]
                if bone_name_detected_new.lower() == bone_name_target:
                    # print('No need to add new bone to save')
                    continue

            # If the source bone got detected but the target bone got changed, save the target bone into the custom list
            if bone_name_target not in bone_detection_list_custom[bone_name_key_detected]:
                bone_detection_list_custom[bone_name_key_detected] = [bone_name_target] + bone_detection_list_custom[bone_name_key_detected]
            continue

        # If it is a completely new pair of bones or a spine bone, add it as a new bone to the list
        bone_detection_list_custom['custom_bone_' + bone_name_source] = [bone_name_source, bone_name_target]

    # Save the updated custom list locally and update
    save_to_file_and_update()

'''
def save_retargeting_to_list(target_armature):
    #global bone_detection_list, bone_detection_list_custom
    armature_target = target_armature
    retargeting_dict = detect_retarget_bones()

    for bone_item in bpy.context.scene.rsl_retargeting_bone_list:
        if not bone_item.bone_name_source or not bone_item.bone_name_target:
            continue

        bone_name_key = bone_item.bone_name_key
        bone_name_source = bone_item.bone_name_source.lower()
        bone_name_target = bone_item.bone_name_target.lower()
        bone_name_target_detected, bone_name_key_detected = retargeting_dict[bone_item.bone_name_source]

        if bone_name_target_detected == bone_item.bone_name_target:
            continue

        if bone_name_key_detected and bone_name_key_detected != 'spine':
            if not bone_detection_list_custom.get(bone_name_key_detected):
                bone_detection_list_custom[bone_name_key_detected] = []

            # TODO Idea: If a target bone got detected but was removed and left empty, add it to an ignore list. So if that exact match-up gets detected again, leave it empty

            # If the detected target is in the custom bones list but it got changed, remove it from the list. If the new bone gets detected automatically now, don't add it to the custom list
            if bone_name_target_detected.lower() in bone_detection_list_custom[bone_name_key_detected]:
                if bone_name_key_detected.startswith('custom_bone_') and len(bone_detection_list_custom[bone_name_key_detected]) == 2:
                    bone_detection_list_custom.pop(bone_name_key_detected)
                else:
                    bone_detection_list_custom[bone_name_key_detected].remove(bone_name_target_detected.lower())

                # Update the bone detection list in order to correctly figure out if the new selected bone needs to be saved
                bone_detection_list = combine_lists(bone_detection_list_unmodified, bone_detection_list_custom)

                retargeting_dict = detect_retarget_bones()
                bone_name_detected_new, _ = retargeting_dict[bone_item.bone_name_source]
                if bone_name_detected_new.lower() == bone_name_target:
                    # print('No need to add new bone to save')
                    continue

            # If the source bone got detected but the target bone got changed, save the target bone into the custom list
            if bone_name_target not in bone_detection_list_custom[bone_name_key_detected]:
                bone_detection_list_custom[bone_name_key_detected] = [bone_name_target] + bone_detection_list_custom[bone_name_key_detected]
            continue

        # If it is a completely new pair of bones or a spine bone, add it as a new bone to the list
        bone_detection_list_custom['custom_bone_' + bone_name_source] = [bone_name_source, bone_name_target]

    # Save the updated custom list locally and update
    save_to_file_and_update()
'''



def save_to_file_and_update():
    save_custom_to_file()
    load_detection_lists()


def save_custom_to_file(file_path=custom_bone_list_file):
    new_custom_list = clean_custom_list()
    print('To File:', new_custom_list)

    if not os.path.isdir(custom_bones_dir):
        os.mkdir(custom_bones_dir)

    with open(file_path, 'w', encoding="utf8") as outfile:
        json.dump(new_custom_list, outfile, ensure_ascii=False, indent=4)


def load_custom_lists_from_file(file_path=custom_bone_list_file):
    custom_bone_list = {}
    try:
        with open(file_path, encoding="utf8") as file:
            custom_bone_list = json.load(file)
    except FileNotFoundError:
        print('Custom bone list not found.')
    except json.decoder.JSONDecodeError:
        print("Custom bone list is not a valid json file!")

    if custom_bone_list.get('rokoko_custom_names') is None or custom_bone_list.get('version') is None or custom_bone_list.get('bones') is None or custom_bone_list.get('shapes') is None:
        print("Custom name list file is not a valid name list file")
        return {}, {}

    custom_bone_list.pop('rokoko_custom_names')
    custom_bone_list.pop('version')

    return custom_bone_list.get('bones'), custom_bone_list.get('shapes')


def clean_custom_list():
    new_custom_list = {
        'rokoko_custom_names':  True,
        'version': 1,
        'bones': {},
        'shapes': {}
    }

    new_bone_list = {}
    new_shape_list = {}

    # Remove all empty fields and make all custom fields lowercase
    for key, values in bone_detection_list_custom.items():
        if not values:
            continue

        for i in range(len(values)):
            values[i] = values[i].lower()

        new_bone_list[key] = values

    # Remove all empty fields and make all custom fields lowercase
    for key, values in shape_detection_list_custom.items():
        if not values:
            continue

        for i in range(len(values)):
            values[i] = values[i].lower()

        new_shape_list[key] = values

    new_custom_list['bones'] = new_bone_list
    new_custom_list['shapes'] = new_shape_list

    return new_custom_list



def import_custom_list(directory, file_name):
    global bone_detection_list_custom, shape_detection_list_custom

    file_path = os.path.join(directory, file_name)
    new_custom_bone_list, new_custom_shape_list = load_custom_lists_from_file(file_path=file_path)

    # Merge the new and old custom bone lists
    for key, bones in bone_detection_list_custom.items():
        if not new_custom_bone_list.get(key):
            new_custom_bone_list[key] = []

        for bone in new_custom_bone_list[key]:
            if bone in bones:
                bones.remove(bone)

        new_custom_bone_list[key] += bones

    # Merge the new and old custom shape lists
    for key, shapes in shape_detection_list_custom.items():
        if not new_custom_shape_list.get(key):
            new_custom_shape_list[key] = []

        for shape in new_custom_shape_list[key]:
            if shape in shapes:
                shapes.remove(shape)

        new_custom_shape_list[key] += shapes

    bone_detection_list_custom = new_custom_bone_list
    shape_detection_list_custom = new_custom_shape_list


def export_custom_list2(directory):
    file_path = os.path.join(directory, 'custom_bone_list.json')

    i = 1
    while os.path.isfile(file_path):
        file_path = os.path.join(directory, 'custom_bone_list' + str(i) + '.json')
        i += 1

    save_custom_to_file(file_path=file_path)

    return os.path.basename(file_path)


def export_custom_list(file_path):
    if not bone_detection_list_custom and not shape_detection_list_custom:
        return None

    save_custom_to_file(file_path=file_path)
    return os.path.basename(file_path)


def delete_custom_bone_list():
    global bone_detection_list_custom
    bone_detection_list_custom = {}
    save_to_file_and_update()


def delete_custom_shape_list():
    global shape_detection_list_custom
    shape_detection_list_custom = {}
    save_to_file_and_update()


def get_bone_list():
    return bone_detection_list


def get_custom_bone_list():
    return bone_detection_list_custom


def get_shape_list():
    return shape_detection_list


def get_custom_shape_list():
    return shape_detection_list_custom


def standardize_bone_name(name):
    # List of chars to replace if they are at the start of a bone name
    starts_with = [
        ('_', ''),
        ('ValveBiped_', ''),
        ('Valvebiped_', ''),
        ('Bip1_', 'Bip_'),
        ('Bip01_', 'Bip_'),
        ('Bip001_', 'Bip_'),
        ('Character1_', ''),
        ('HLP_', ''),
        ('JD_', ''),
        ('JU_', ''),
        ('Armature|', ''),
        ('Bone_', ''),
        ('C_', ''),
        ('Cf_S_', ''),
        ('Cf_J_', ''),
        ('G_', ''),
        ('Joint_', ''),
        ('DEF_', ''),
    ]

    # Standardize names
    # Make all the underscores!
    name = name.replace(' ', '_') \
        .replace('-', '_') \
        .replace('.', '_') \
        .replace('____', '_') \
        .replace('___', '_') \
        .replace('__', '_') \

    # Replace if name starts with specified chars
    for replacement in starts_with:
        if name.startswith(replacement[0]):
            name = replacement[1] + name[len(replacement[0]):]

    # Remove digits from the start
    name_split = name.split('_')
    if len(name_split) > 1 and name_split[0].isdigit():
        name = name_split[1]

    # Specific condition
    name_split = name.split('"')
    if len(name_split) > 3:
        name = name_split[1]

    # Another specific condition
    if ':' in name:
        for i, split in enumerate(name.split(':')):
            if i == 0:
                name = ''
            else:
                name += split

    # Remove S0 from the end
    if name[-2:] == 'S0':
        name = name[:-2]

    if name[-4:] == '_Jnt':
        name = name[:-4]

    return name.lower()


def detect_shape(obj, shape_name_key):
    # Go through the target mesh and search for shapekey that fit the main shapekey
    found_shape_name = ''
    is_custom = False

    for shapekey in obj.data.shape_keys.key_blocks:
        if is_custom:  # If a custom shapekey name was found, stop searching. it has priority
            break

        if shape_detection_list_custom.get(shape_name_key):
            for shape_name_detected in shape_detection_list_custom[shape_name_key]:
                if shape_name_detected == shapekey.name.lower():
                    found_shape_name = shapekey.name
                    is_custom = True
                    break

        if found_shape_name and shape_name_key != 'chest':  # If a shape_name was found, only continue looking for custom shapekey names, they have priority
            continue

        for shape_name_detected in shape_detection_list[shape_name_key]:
            if shape_name_detected == shapekey.name.lower():
                found_shape_name = shapekey.name
                break

        # If nothing was found, check if the shapekey names match exactly
        if not found_shape_name and shape_name_key.lower() == shapekey.name.lower():
            found_shape_name = shapekey.name

    return found_shape_name


def detect_bone(obj, bone_name_key, bone_name_source=None):
    # Go through the target armature and search for bones that fit the main source bone
    found_bone_name = ''
    is_custom = False

    if not bone_name_source:
        bone_name_source = bone_name_key

    for bone in obj.pose.bones:
        if is_custom:  # If a custom bone name was found, stop searching. it has priority
            break

        if bone_detection_list_custom.get(bone_name_key):
            for bone_name_detected in bone_detection_list_custom[bone_name_key]:
                if bone_name_detected == bone.name.lower():
                    found_bone_name = bone.name
                    is_custom = True
                    break

        if found_bone_name and bone_name_key != 'chest':  # If a bone_name was found, only continue looking for custom bone names, they have priority
            continue

        for bone_name_detected in bone_detection_list[bone_name_key]:
            if bone_name_detected == standardize_bone_name(bone.name):
                found_bone_name = bone.name
                break

        # If nothing was found, check if the bone names match exactly
        if not found_bone_name and bone_name_source.lower() == bone.name.lower():
            found_bone_name = bone.name

    return found_bone_name


def detect_retarget_bones(armature_source, armature_target):
    bone_list_animated = []
    retargeting_dict = {}
    armature_source# = retargeting.get_source_armature()
    armature_target# = retargeting.get_target_armature()

    # Get all bones from the animation
    for fc in armature_source.animation_data.action.fcurves:
        bone_name = fc.data_path.split('"')
        if len(bone_name) == 3 and bone_name[1] not in bone_list_animated:
            bone_list_animated.append(bone_name[1])

    # Check if this animation is from Rokoko Studio. Ignore certain bones in that case
    is_rokoko_animation = False
    if 'newton' in bone_list_animated and 'RightFinger1Tip' in bone_list_animated and 'HeadVertex' in bone_list_animated and 'LeftFinger2Metacarpal' in bone_list_animated:
        is_rokoko_animation = True
        # print('Rokoko animation detected')

    spines_source = []
    spines_target = []
    found_main_bones = []

    # Then add all the bones to the list
    for bone_name in bone_list_animated:
        if is_rokoko_animation and bone_name in ignore_rokoko_retargeting_bones:
            continue

        bone_item_source = bone_name
        bone_item_target = ''
        main_bone_name = ''
        standardized_bone_name_source = standardize_bone_name(bone_name)

        # Find the main bone name of the source bone
        for bone_main, bone_values in bone_detection_list.items():
            if bone_main == 'chest':  # Ignore chest bones, these are only used for live data
                continue
            if bone_main in found_main_bones:  # Only find main bones once, except for spines
                continue
            if bone_name.lower() in bone_values or standardized_bone_name_source in bone_values or standardized_bone_name_source == bone_main.lower():
                main_bone_name = bone_main
                if main_bone_name != 'spine':  # Ignore the spine bones for now, so that it can add the custom spine bones first
                    found_main_bones.append(main_bone_name)
                    break

        # Add the bone to the retargeting list
        retargeting_dict[bone_item_source] = (bone_item_target, main_bone_name)

        # If no main bone name was found, continue
        if not main_bone_name:
            continue

        # If it's a spine bone, add it to the list for later fixing
        if main_bone_name == 'spine':
            spines_source.append(bone_name)
            continue

        # If it's a custom spine/chest bone, add it to the spine list nonetheless
        custom_main_bone = main_bone_name.startswith('custom_bone_')
        if custom_main_bone and standardize_bone_name(main_bone_name.replace('custom_bone_', '')) in bone_detection_list['spine']:
            spines_source.append(bone_name)

        # Go through the target armature and search for bones that fit the main source bone
        bone_item_target = detect_bone(armature_target, main_bone_name, bone_name_source=bone_item_source)

        # Add the bone to the retargeting list again
        retargeting_dict[bone_item_source] = (bone_item_target, main_bone_name)

    # Add target spines to list for later fixing
    for bone in armature_target.pose.bones:
        bone_name_standardized = standardize_bone_name(bone.name)
        if bone_name_standardized in bone_detection_list['spine']:
            spines_target.append(bone.name)

    # Fix spine auto detection
    if spines_target and spines_source:
        # print(spines_source)
        spine_dict = {}

        i = 0
        for spine in reversed(spines_source):
            i += 1
            if i == len(spines_target):
                break
            spine_dict[spine] = spines_target[-i]

        spine_dict[spines_source[0]] = spines_target[0]

        # Fill in fixed spines into unfilled matches
        for spine_source, spine_target in spine_dict.items():
            for bone_source, bone_values in retargeting_dict.items():
                bone_target, bone_key = bone_values
                if bone_source == spine_source and not bone_target:
                    retargeting_dict[bone_source] = (spine_target, bone_key)
                    break

    return retargeting_dict

'''
def detect_retarget_bones(source_armature, target_armature):
    bone_list_animated = []
    retargeting_dict = {}
    armature_source = source_armature
    armature_target = target_armature
    bone_detection_list, shape_detection_list = load_detection_lists()


    # Get all bones from the animation
    for fc in armature_source.animation_data.action.fcurves:
        bone_name = fc.data_path.split('"')
        if len(bone_name) == 3 and bone_name[1] not in bone_list_animated:
            bone_list_animated.append(bone_name[1])

    # Check if this animation is from Rokoko Studio. Ignore certain bones in that case
    is_rokoko_animation = False
    if 'newton' in bone_list_animated and 'RightFinger1Tip' in bone_list_animated and 'HeadVertex' in bone_list_animated and 'LeftFinger2Metacarpal' in bone_list_animated:
        is_rokoko_animation = True
        # print('Rokoko animation detected')

    spines_source = []
    spines_target = []
    found_main_bones = []

    # Then add all the bones to the list
    for bone_name in bone_list_animated:
        if is_rokoko_animation and bone_name in ignore_rokoko_retargeting_bones:
            continue

        bone_item_source = bone_name
        bone_item_target = ''
        main_bone_name = ''
        standardized_bone_name_source = standardize_bone_name(bone_name)

        # Find the main bone name of the source bone
        for bone_main, bone_values in bone_detection_list.items():
            if bone_main == 'chest':  # Ignore chest bones, these are only used for live data
                continue
            if bone_main in found_main_bones:  # Only find main bones once, except for spines
                continue
            if bone_name.lower() in bone_values or standardized_bone_name_source in bone_values or standardized_bone_name_source == bone_main.lower():
                main_bone_name = bone_main
                if main_bone_name != 'spine':  # Ignore the spine bones for now, so that it can add the custom spine bones first
                    found_main_bones.append(main_bone_name)
                    break

        # Add the bone to the retargeting list
        retargeting_dict[bone_item_source] = (bone_item_target, main_bone_name)

        # If no main bone name was found, continue
        if not main_bone_name:
            continue

        # If it's a spine bone, add it to the list for later fixing
        if main_bone_name == 'spine':
            spines_source.append(bone_name)
            continue

        # If it's a custom spine/chest bone, add it to the spine list nonetheless
        custom_main_bone = main_bone_name.startswith('custom_bone_')
        if custom_main_bone and standardize_bone_name(main_bone_name.replace('custom_bone_', '')) in bone_detection_list['spine']:
            spines_source.append(bone_name)

        # Go through the target armature and search for bones that fit the main source bone
        bone_item_target = detect_bone(armature_target, main_bone_name, bone_name_source=bone_item_source)

        # Add the bone to the retargeting list again
        retargeting_dict[bone_item_source] = (bone_item_target, main_bone_name)

    # Add target spines to list for later fixing
    for bone in armature_target.pose.bones:
        bone_name_standardized = standardize_bone_name(bone.name)
        if bone_name_standardized in bone_detection_list['spine']:
            spines_target.append(bone.name)

    # Fix spine auto detection
    if spines_target and spines_source:
        # print(spines_source)
        spine_dict = {}

        i = 0
        for spine in reversed(spines_source):
            i += 1
            if i == len(spines_target):
                break
            spine_dict[spine] = spines_target[-i]

        spine_dict[spines_source[0]] = spines_target[0]

        # Fill in fixed spines into unfilled matches
        for spine_source, spine_target in spine_dict.items():
            for bone_source, bone_values in retargeting_dict.items():
                bone_target, bone_key = bone_values
                if bone_source == spine_source and not bone_target:
                    retargeting_dict[bone_source] = (spine_target, bone_key)
                    break

    return retargeting_dict
'''




def load_detection_lists():
    global bone_detection_list, bone_detection_list_unmodified, bone_detection_list_custom, shape_detection_list, shape_detection_list_unmodified, shape_detection_list_custom

    # Create the lists from the internal naming lists
    bone_detection_list_unmodified = create_internal_bone_list()
    shape_detection_list_unmodified = create_internal_shape_list()

    # Load the custom naming lists from the file
    bone_detection_list_custom, shape_detection_list_custom = load_custom_lists_from_file(r"C:/users/admin/Downloads/FAToCMU.json")

    # Combine custom and internal lists
    bone_detection_list = combine_lists(bone_detection_list_unmodified, bone_detection_list_custom)
    shape_detection_list = combine_lists(shape_detection_list_unmodified, shape_detection_list_custom)

    # Print the whole bone list
    # print_bone_detection_list()
'''
def load_detection_lists():
    #global bone_detection_list, bone_detection_list_unmodified, bone_detection_list_custom, shape_detection_list, shape_detection_list_unmodified, shape_detection_list_custom

    # Create the lists from the internal naming lists
    bone_detection_list_unmodified = create_internal_bone_list()
    shape_detection_list_unmodified = create_internal_shape_list()
    print("created bone_detection_list_unmodified: ", bone_detection_list_unmodified)
    print("created shape_detection_list_unmodified: ", shape_detection_list_unmodified)
    # Load the custom naming lists from the file
    bone_detection_list_custom, shape_detection_list_custom = load_custom_lists_from_file()

    # Combine custom and internal lists
    bone_detection_list = combine_lists(bone_detection_list_unmodified, bone_detection_list_custom)
    shape_detection_list = combine_lists(shape_detection_list_unmodified, shape_detection_list_custom)

    return bone_detection_list, shape_detection_list
'''


def create_internal_bone_list():
    new_bone_list = {}

    for bone_key, bone_values in bone_list.items():
        # Add the bones to the list if no side indicator is found
        if 'left' not in bone_key:
            new_bone_list[bone_key] = [bone_value.lower() for bone_value in bone_values]
            if bone_key == 'spine':
                new_bone_list['chest'] = [bone_value.lower() for bone_value in bone_values]
            continue

        # Add bones to the list that are two sided
        bone_values_left = []
        bone_values_right = []

        for bone_name in bone_values:
            bone_name = bone_name.lower()

            if '\l' in bone_name:
                for replacement in ['l', 'left', 'r', 'right']:
                    bone_name_new = bone_name.replace('\l', replacement)

                    # Debug if duplicates are found
                    if bone_name_new in bone_values_left or bone_name_new in bone_values_right:
                        print('Duplicate autodetect bone entry:', bone_name, bone_name_new)
                        continue

                    if 'l' in replacement:
                        bone_values_left.append(bone_name_new)
                    else:
                        bone_values_right.append(bone_name_new)

        bone_key_left = bone_key
        bone_key_right = bone_key.replace('left', 'right')

        new_bone_list[bone_key_left] = bone_values_left
        new_bone_list[bone_key_right] = bone_values_right

    return new_bone_list
'''
def create_internal_bone_list():
    new_bone_list = {}

    for bone_key, bone_values in bone_list.items():
        # Add the bones to the list if no side indicator is found
        if 'left' not in bone_key:
            new_bone_list[bone_key] = [bone_value.lower() for bone_value in bone_values]
            if bone_key == 'spine':
                new_bone_list['chest'] = [bone_value.lower() for bone_value in bone_values]
            continue

        # Add bones to the list that are two sided
        bone_values_left = []
        bone_values_right = []

        for bone_name in bone_values:
            bone_name = bone_name.lower()

            if '\l' in bone_name:
                for replacement in ['l', 'left', 'r', 'right']:
                    bone_name_new = bone_name.replace('\l', replacement)

                    # Debug if duplicates are found
                    if bone_name_new in bone_values_left or bone_name_new in bone_values_right:
                        print('Duplicate autodetect bone entry:', bone_name, bone_name_new)
                        continue

                    if 'l' in replacement:
                        bone_values_left.append(bone_name_new)
                    else:
                        bone_values_right.append(bone_name_new)

        bone_key_left = bone_key
        bone_key_right = bone_key.replace('left', 'right')

        new_bone_list[bone_key_left] = bone_values_left
        new_bone_list[bone_key_right] = bone_values_right

    return new_bone_list
'''

def create_internal_shape_list():
    new_shape_list = {}

    for shape_key, shape_names in shape_list.items():
        new_shape_list[shape_key] = [shape_key.lower()] + [shape_name.lower() for shape_name in shape_names]

    return new_shape_list
'''
def create_internal_shape_list():
    new_shape_list = {}

    for shape_key, shape_names in shape_list.items():
        new_shape_list[shape_key] = [shape_key.lower()] + [shape_name.lower() for shape_name in shape_names]

    return new_shape_list
'''

def combine_lists(internal_list, custom_list):
    combined_list = {}

    # Set dictionary structure
    for key in internal_list.keys():
        combined_list[key] = []

    # Load in custom shapes into the dictionary
    for key, values in custom_list.items():
        combined_list[key] = []
        for value in values:
            combined_list[key].append(value.lower())

    # Load in internal bones
    for key, values in internal_list.items():
        for value in values:
            combined_list[key].append(value)

    return combined_list


def print_bone_detection_list():
    # for key, values in bone_detection_list.items():
    #     print(key, values)
    #     print()
    print('CUSTOM')
    for key, values in bone_detection_list_custom.items():
        print(key, values)
        print('--> ', bone_detection_list[key])
        print()

    # print('SHAPES')
    # for key, values in shape_detection_list.items():
    #     print(key, values)

    print('CUSTOM')
    for key, values in shape_detection_list_custom.items():
        print(key, values)
        print('--> ', shape_detection_list[key])
        print()
    print()

import collections
BoneListItemNoUI = collections.namedtuple("BoneListItemNoUI",["bone_name_source", "bone_name_target", "bone_name_key"])



def retarget_main(source_armature_name, target_armature_name):
    #hard code in params for now
    source_armature = bpy.context.scene.objects[source_armature_name]#"Armature"
    target_armature = bpy.context.scene.objects[target_armature_name]#"Bip01"

    load_detection_lists()
    save_retargeting_to_list(source_armature, target_armature)

    retargeting_dict = detect_retarget_bones(source_armature, target_armature)
    #print("retarget_bones_dict: ", )
    animRetargeter = RetargetAnimation()

    retargeting_bone_list = []
    for bone_source, bone_values in retargeting_dict.items():
        bone_target, bone_key = bone_values
        bone_item = BoneListItemNoUI(bone_source, bone_target, bone_key)
        retargeting_bone_list.append(bone_item)
        #bone_item = context.scene.rsl_retargeting_bone_list.add()
        #bone_item.bone_name_key = bone_key
        #bone_item.bone_name_source = bone_source
        #bone_item.bone_name_target = bone_target

    #retargeting_bone_list = [bone for bone in target_armature.data.bones]
    animRetargeter.execute(source_armature, target_armature, True, retargeting_bone_list)



