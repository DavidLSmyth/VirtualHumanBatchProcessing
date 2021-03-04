import os
import sys
from typing import *
import inspect
import re
from collections import namedtuple
import shutil

try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

sys.path.append('.')
from utils.configure_paths import configure_paths
from scene_manager.scene_manager import set_empty_scene, reset_blend
from format_converters import import_file, export_file
from format_converters.ImportExportParamManager import ImportArgsManager, ExportArgsManager

configure_paths()


def merge_all_meshes():
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]
    bpy.ops.object.join()


def delete_armature():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['Armature'].select_set(True)  # 2.8+
    bpy.ops.object.delete()


def delete_nondiffuse_materials():
    for material in bpy.data.materials:
        # not sure what this is but can be skipped
        if material.name == "Dots Stroke":
            continue
        bsdf = material.node_tree.nodes.get("Principled BSDF")

        # delete nodes that don't go into base color
        for node in material.node_tree.nodes:
            # print("Node: ", node)
            for input in node.inputs:
                for link in input.links:
                    if input.name not in ["Base Color"] and link.from_node.name != "Principled BSDF":
                        print("deleting ", link.from_node)
                        material.node_tree.nodes.remove(link.from_node)

        for node in material.node_tree.nodes:
            try:
                print("node image: ", node.image)
                bpy.ops.file.unpack_item(id_name=node.image.name)
                print("sucessfully unpacked")
            except Exception as e:
                pass


def combine_materials():
    '''
    For a given mesh, invokes the material combiner addon. Directory is hard-coded in the add-on
    :return:
    '''
    try:
        bpy.ops.smc.refresh_ob_data()
        # bpy.context.space_data.params.directory = "D:\\SAUCEFiles\\MixamoCharacters\\MixamoChars\\unpackedTextures"

        bpy.ops.smc.combiner("INVOKE_DEFAULT")
    except RuntimeError as e:
        raise e


def gen_obj_single_texture(fbx_file_path, obj_file_path, frame_list):
    # 1. read in fbx file
    importArgsManager = ImportArgsManager(import_file_type='fbx')
    importArgsManager.set_import_arg("filepath", fbx_file_path)
    import_file(fbx_file_path, importArgsManager.get_import_args_dict(), verbose=True)

    # 2. merge meshes and delete armature
    # delete_armature()
    # merge_all_meshes()

    # 3. Delete unneeded materials
    #delete_nondiffuse_materials()

    # 4. Combine materials
    combine_materials()

    # 5. Export obj
    # r"D:\SAUCEFiles\MixamoCharacters\MixamoCharsObj"
    obj_file_name = obj_file_path
    exportArgsManager = ExportArgsManager(export_file_type="obj")
    exportArgsManager.set_export_arg("use_normals", True)
    exportArgsManager.set_export_arg("use_materials", True)
    exportArgsManager.set_export_arg("path_mode", "COPY")

    if frame_list:
        for frame in frame_list:
            bpy.context.scene.frame_set(frame)

            exportArgsManager.set_export_arg("filepath", obj_file_name)
            export_file(obj_file_name, kwargs=exportArgsManager.get_export_args_dict(), verbose=True)


def gen_single_obj_texture_folder(fbx_folder, obj_folder, frame_list):
    for fbx_file in os.listdir(fbx_folder):
        print("Processing ", fbx_file)
        gen_obj_single_texture(os.path.join(fbx_folder, fbx_file),
                               os.path.join(obj_folder, os.path.splitext(fbx_file)[0] + ".obj"), frame_list)
        set_empty_scene()


def main():
    # 1. read in fbx file

    fbx_folder_loc = r"D:\TCDFiles\3dGeom\SquatData\SquatMeshes\fbx"
    obj_folder_loc = r"D:\SAUCEFiles\MixamoCharacters\MixamoChars\unpackedTextures"
    mesh_name = "regina"
    # bpy.ops.wm.read_factory_settings(use_empty = True)
    # bpy.ops.wm.read_factory_settings(use_empty=True)
    set_empty_scene()
    frames_list = []

    # files_to_process = ['Andromeda.fbx', 'Brian.fbx', 'Bryce.fbx', 'David.fbx', 'Douglas.fbx', 'Jody.fbx', 'Joe.fbx', 'Josh.fbx', 'Kate.fbx', 'Leonard.fbx',
    #                    'Lewis.fbx', 'Liam.fbx', 'Louise.fbx', 'Malcolm.fbx', 'Martha.fbx', 'Megan.fbx', 'Pete.fbx', 'Racer.fbx', 'Regina.fbx','Remy.fbx', 'Shannon.fbx', 'Sophie.fbx',
    #                    'Stefani.fbx', 'Suzie.fbx']
    files_to_process = open(r"C:\Users\admin\3DGeom\blender3dgscripts\cleanup_scripts\combine_textures\RocketboxSquat_fbx_file_loc.txt", 'r').readlines()
    files_to_process = [f.replace("\n", "") for f in files_to_process]

    #files_to_process = ['Lewis.fbx']

    # gen_obj_single_texture(os.path.join(fbx_folder_loc, "{}.fbx".format(mesh_name)), os.path.join(obj_folder_loc, "{}.obj".format(mesh_name)))

    #files_to_process = [fbx_folder_loc + '\\' + file for file in os.listdir(fbx_folder_loc)]

    for file in files_to_process:
        assert os.path.isfile(file), file

    for mesh_name in files_to_process:
        mesh_base_name = os.path.basename(mesh_name)[:-4]

        gen_obj_single_texture(mesh_name,
                               os.path.join(obj_folder_loc, "{}.obj".format(mesh_base_name)))
        # for file in os.listdir(obj_folder_loc):
        #    if "Atlas_" in file:
        #        shutil.move(os.path.join(obj_folder_loc, file), os.path.join(obj_folder_loc, mesh_name[:-4] + ".png"))
        newdir = os.path.join(obj_folder_loc, mesh_base_name)
        os.mkdir(newdir)

        for file in [f for f in os.listdir(obj_folder_loc) if os.path.isfile(os.path.join(obj_folder_loc, f))]:
            shutil.move(os.path.join(obj_folder_loc, file), newdir)

        set_empty_scene()
        reset_blend()


if __name__ == '__main__':
    main()

    # blender --python cleanup_scripts\combine_textures\test.py
