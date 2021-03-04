# blender --background --python 10_mocap.py --render-frame 1 -- </path/to/input/bvh> </path/to/output/directory>/<name> <resolution_percentage> <num_samples>
# ffmpeg -r 24 -i </path/to/output/directory>/<name>%04d.png -pix_fmt yuv420p out.mp4

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils
import external.cc0assetsloader as loader


def create_armature_from_bvh(bvh_path: str) -> bpy.types.Object:
    bpy.ops.import_anim.bvh(filepath=bvh_path,
                            axis_forward='-Z',
                            axis_up='Y',
                            target='ARMATURE',
                            global_scale=0.056444,
                            frame_start=1,
                            use_fps_scale=True,
                            update_scene_fps=False,
                            update_scene_duration=True)
    armature = bpy.context.object
    return armature


def build_scene(scene: bpy.types.Scene, input_bvh_path: str) -> bpy.types.Object:
    loader.build_pbr_textured_nodes_from_name("Concrete07", scale=(0.25, 0.25, 0.25))

    mat = utils.add_material("BlueMetal", use_nodes=True, make_node_tree_empty=True)
    output_node = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    principled_node = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_node.inputs['Base Color'].default_value = (0.1, 0.2, 0.7, 1.0)
    principled_node.inputs['Metallic'].default_value = 0.9
    principled_node.inputs['Roughness'].default_value = 0.1
    mat.node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    utils.arrange_nodes(mat.node_tree)

    armature = create_armature_from_bvh(bvh_path=input_bvh_path)
    armature_mesh = utils.create_armature_mesh(scene, armature, 'Mesh')
    armature_mesh.data.materials.append(mat)

    current_object = utils.create_plane(size=16.0, name="Floor")
    current_object.data.materials.append(bpy.data.materials["Concrete07"])

    current_object = utils.create_plane(size=16.0, name="Wall")
    current_object.data.materials.append(bpy.data.materials["Concrete07"])
    current_object.location = (0.0, 6.0, 0.0)
    current_object.rotation_euler = (0.5 * math.pi, 0.0, 0.0)

    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.8))
    focus_target = bpy.context.object
    utils.add_copy_location_constraint(copy_to_object=focus_target,
                                       copy_from_object=armature,
                                       use_x=True,
                                       use_y=True,
                                       use_z=False,
                                       bone_name='Hips')

    return focus_target


# Args
input_bvh_path = str(sys.argv[sys.argv.index('--') + 1])  # "./assets/motion/102_01.bvh"
output_file_path = str(sys.argv[sys.argv.index('--') + 2])  # "./"
resolution_percentage = int(sys.argv[sys.argv.index('--') + 3])  # 100
num_samples = int(sys.argv[sys.argv.index('--') + 4])  # 128

# Parameters
hdri_path = "./assets/HDRIs/green_point_park_2k.hdr"

# Scene Building
scene = bpy.data.scenes["Scene"]
world = scene.world

## Reset
utils.clean_objects()

# Animation Setting
utils.set_animation(scene, fps=24, frame_start=1, frame_end=40)  # frame_end will be overriden later

## Scene
focus_target_object = build_scene(scene, input_bvh_path)

## Camera
camera_object = utils.create_camera(location=(0.0, -10.0, 1.0))

utils.add_copy_location_constraint(copy_to_object=camera_object,
                                   copy_from_object=focus_target_object,
                                   use_x=True,
                                   use_y=False,
                                   use_z=False)
utils.add_track_to_constraint(camera_object, focus_target_object)
utils.set_camera_params(camera_object.data, focus_target_object)

## Lights
utils.build_environment_texture_background(world, hdri_path)

## Composition
utils.build_scene_composition(scene)

# Render Setting
utils.set_output_properties(scene, resolution_percentage, output_file_path)
utils.set_cycles_renderer(scene, camera_object, num_samples, use_motion_blur=True)
