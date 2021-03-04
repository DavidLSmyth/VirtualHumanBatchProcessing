# blender --background --python 07_texturing.py --render-frame 1 -- </path/to/output/image> <resolution_percentage> <num_samples>

import bpy
import sys
import math
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import utils
import external.cc0assetsloader as loader


def set_scene_objects():
    loader.build_pbr_textured_nodes_from_name("Leather05")
    loader.build_pbr_textured_nodes_from_name("Metal07")
    loader.build_pbr_textured_nodes_from_name("Fabric02")
    loader.build_pbr_textured_nodes_from_name("Marble01")

    left_object, center_object, right_object = utils.create_three_smooth_monkeys()

    left_object.data.materials.append(bpy.data.materials["Leather05"])
    center_object.data.materials.append(bpy.data.materials["Metal07"])
    right_object.data.materials.append(bpy.data.materials["Fabric02"])

    current_object = utils.create_plane(size=12.0, name="Floor")
    current_object.data.materials.append(bpy.data.materials["Marble01"])

    current_object = utils.create_plane(size=12.0,
                                        location=(0.0, 4.0, 0.0),
                                        rotation=(math.pi * 90.0 / 180.0, 0.0, 0.0),
                                        name="Wall")
    current_object.data.materials.append(bpy.data.materials["Marble01"])

    bpy.ops.object.empty_add(location=(0.0, -0.70, 1.0))
    focus_target = bpy.context.object
    return focus_target


def set_camera_params(camera, dof_target):
    camera.data.sensor_fit = 'HORIZONTAL'
    camera.data.sensor_width = 36.0
    camera.data.sensor_height = 24.0
    camera.data.lens = 72
    camera.data.dof_object = dof_target
    camera.data.cycles.aperture_type = 'RADIUS'
    camera.data.cycles.aperture_size = 0.100
    camera.data.cycles.aperture_blades = 6


# Args
output_file_path = str(sys.argv[sys.argv.index('--') + 1])
resolution_percentage = int(sys.argv[sys.argv.index('--') + 2])
num_samples = int(sys.argv[sys.argv.index('--') + 3])

# Parameters
hdri_path = "./assets/HDRIs/green_point_park_2k.hdr"

# Scene Building
scene = bpy.data.scenes["Scene"]
world = scene.world

## Reset
utils.clean_objects()

## Suzannes
focus_target = set_scene_objects()

## Camera
bpy.ops.object.camera_add(location=(0.0, -16.0, 2.0))
camera_object = bpy.context.object

utils.add_track_to_constraint(camera_object, focus_target)
utils.set_camera_params(camera_object.data, focus_target, lens=85, fstop=0.5)

## Lights
utils.build_environment_texture_background(world, hdri_path)

## Composition
utils.build_scene_composition(scene)

# Render Setting
utils.set_output_properties(scene, resolution_percentage, output_file_path)
utils.set_cycles_renderer(scene, camera_object, num_samples)
