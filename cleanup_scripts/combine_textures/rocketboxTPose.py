import os
import sys
from typing import *
import inspect
import re
from collections import namedtuple
import shutil
import glob
import re
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
from cleanup_scripts.combine_textures.png2jpg import png2jpg

configure_paths()

def remove_duplicate_mtl(obj_folder):
    '''
    Assumes that there are duplicate png & mtl files in the given folder with objs. This function deletes the duplicate png & mtl and edits the corresponding obj files
    :return:
    '''
    print(os.listdir(obj_folder))
    mtl_files = list(filter(lambda x: os.path.splitext(x)[1] == ".mtl", os.listdir(obj_folder)))
    obj_files = list(filter(lambda x: os.path.splitext(x)[1] == ".obj", os.listdir(obj_folder)))
    png_files = list(filter(lambda x: os.path.splitext(x)[1] == ".png", os.listdir(obj_folder)))

    print("obj_folder: ",obj_folder)
    print("mtl_files: ", mtl_files)
    print("obj_files: ", obj_files)
    print("png_files: ", png_files)

    png_to_keep = png_files[-1]
    mtl_to_keep = mtl_files[-1]

    for png_file in png_files[:-1]:
        os.remove(os.path.join(obj_folder, png_file))
    for mtl_file in mtl_files[:-1]:
        os.remove(os.path.join(obj_folder, mtl_file))

    #rename atlas to rocketbox character name
    rocketbox_char_name = os.path.split(obj_folder)[1]
    print("rocketbox_char_name: ", rocketbox_char_name)
    #png_base_path = os.path.basename(obj_folder)

    new_name = os.path.join(obj_folder, rocketbox_char_name + ".png")
    print("renaming {} to {}".format(os.path.join(obj_folder, png_to_keep), new_name))
    os.rename(os.path.join(obj_folder, png_to_keep), new_name)

    png2jpg(new_name, new_name.replace("png", "jpg"))

    update_mtl_file(os.path.join(obj_folder, mtl_to_keep), rocketbox_char_name)

    for obj_file in obj_files:
        update_obj_file(os.path.join(obj_folder, obj_file), rocketbox_char_name)



def update_mtl_file(mtl_file_loc, rocketbox_char_name):
    mtl_file_read = open(mtl_file_loc, 'r')
    text = mtl_file_read.read()

    updated_text = re.sub("material_atlas_[0-9]+", rocketbox_char_name, text)
    updated_text = re.sub("Atlas_[0-9]+", rocketbox_char_name, updated_text)
    updated_text = re.sub(".png", ".jpg", updated_text)

    mtl_file_read.close()

    mtl_file_edit = open(mtl_file_loc, 'w')
    mtl_file_edit.write(updated_text)
    mtl_file_edit.close()

    # rename png and mtl to rocketbox character name
    #rocketbox_char_name
    new_name = os.path.join(os.path.split(mtl_file_loc)[0], rocketbox_char_name + '.mtl')
    os.rename(mtl_file_loc, new_name)

def update_obj_file(obj_file_loc, rocketbox_char_name):
    '''
    png and mtl should have already been renamed to rocketbox character name
    :param obj_file_loc:
    :param rocketbox_char_name:
    :return:
    '''
    obj_file_read = open(obj_file_loc, 'r')
    text = obj_file_read.read()
    #mtllib Female_Adult_05#angry#frame037.mtl
    updated_text = re.sub("mtllib .*.mtl", "mtllib "+rocketbox_char_name + ".mtl", text)
    updated_text = re.sub("material_atlas_[0-9]+", rocketbox_char_name, updated_text)
    updated_text = re.sub("Atlas_[0-9]+", rocketbox_char_name , updated_text)
    obj_file_read.close()

    obj_file_edit = open(obj_file_loc, 'w')
    obj_file_edit.write(updated_text)
    obj_file_edit.close()


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


def gen_obj_single_texture(fbx_file_path, obj_file_path, frame_list, rocketbox_character_name, animation_name):
    # 1. read in fbx file
    importArgsManager = ImportArgsManager(import_file_type='fbx')
    importArgsManager.set_import_arg("filepath", fbx_file_path)
    import_file(fbx_file_path, importArgsManager.get_import_args_dict(), verbose=True)

    # 2. merge meshes and delete armature
    # delete_armature()
    # merge_all_meshes()

    # 3. Delete unneeded materials
    # delete_nondiffuse_materials()

    # 4. Combine materials
    combine_materials()

    # 5. Export obj
    # r"D:\SAUCEFiles\MixamoCharacters\MixamoCharsObj"
    exportArgsManager = ExportArgsManager(export_file_type="obj")
    exportArgsManager.set_export_arg("use_normals", True)
    exportArgsManager.set_export_arg("use_materials", True)
    exportArgsManager.set_export_arg("path_mode", "COPY")

    if frame_list:
        for frame in frame_list:
            bpy.context.scene.frame_set(frame)
            obj_file_name = os.path.join(obj_file_path, "{}#{}#frame{:003d}.obj".format(rocketbox_character_name, animation_name, frame))
            exportArgsManager.set_export_arg("filepath", obj_file_name)
            export_file(obj_file_name, kwargs=exportArgsManager.get_export_args_dict(), verbose=True)

    #for multiple frames, delete duplicated textures
    #if len(frame_list) > 1:
    #    pngs = glob.glob(obj_file_path +"/*.png")
    #    for png in pngs[:-1]:
    #        os.remove(png)

def gen_single_obj_texture_folder(fbx_folder, obj_folder, frame_list):
    for fbx_file in os.listdir(fbx_folder):
        print("Processing ", fbx_file)
        gen_obj_single_texture(os.path.join(fbx_folder, fbx_file),
                               os.path.join(obj_folder, os.path.splitext(fbx_file)[0] + ".obj"), frame_list)
        set_empty_scene()


def main():
    # 1. read in fbx file

    set_empty_scene()

    #picked to be diverse. Maps animations to frames to export
    frames_mapping = {"angry":[37,350,380],
                      "defeated": [50,55,60,100],
                      "old_man_idle": [20,70,298],
                      "reaction": [2,10,15,20,25,30],
                      "hip_hop_dancing": [2, 10] + [i for i in range(15, 95, 10)],
                      "silly_dancing": [_ for _ in range(10,110, 10)],
                      "rumba_dancing": [_ for _ in range(5,65, 10)],
                      "standing_torch_light_torch": [10,50,120],
                      "using_a_fax_machine": [40,60,80,150,200,300],
                      "bboy_uprock_start": [30,40,50,55],
                      "dodging_right": [5,10,15,20,25]}

    # files_to_process = ['Andromeda.fbx', 'Brian.fbx', 'Bryce.fbx', 'David.fbx', 'Douglas.fbx', 'Jody.fbx', 'Joe.fbx', 'Josh.fbx', 'Kate.fbx', 'Leonard.fbx',
    #                    'Lewis.fbx', 'Liam.fbx', 'Louise.fbx', 'Malcolm.fbx', 'Martha.fbx', 'Megan.fbx', 'Pete.fbx', 'Racer.fbx', 'Regina.fbx','Remy.fbx', 'Shannon.fbx', 'Sophie.fbx',
    #                    'Stefani.fbx', 'Suzie.fbx']
    files_to_process = open(r"C:\Users\admin\3DGeom\blender3dgscripts\cleanup_scripts\combine_textures\rocketboxAdults\rocketboxAdults_retargeted4.txt", 'r').readlines()


    files_to_process = [f.replace("\n", "") for f in files_to_process]

    # files_to_process = ['Lewis.fbx']

    # gen_obj_single_texture(os.path.join(fbx_folder_loc, "{}.fbx".format(mesh_name)), os.path.join(obj_folder_loc, "{}.obj".format(mesh_name)))

    # files_to_process = [fbx_folder_loc + '\\' + file for file in os.listdir(fbx_folder_loc)]

    for file in files_to_process:
        assert os.path.isfile(file), file

    #where to export objs
    obj_folder_loc = r"C:\Users\admin\Documents\3dGeom\ObjMeshesAdults"

    for file_to_process in files_to_process:
        #get the name of the rocketbox character and animation
        base_name = os.path.basename(file_to_process)
        rocketbox_character_name = base_name.split('#')[0].replace("TPose", "")
        animation_name = base_name.split('#')[1]

        obj_file_path = os.path.join(obj_folder_loc, animation_name, rocketbox_character_name)
        gen_obj_single_texture(file_to_process, obj_file_path, frames_mapping[animation_name], rocketbox_character_name, animation_name)
        #after objs have been generated tidy up pngs and mtls
        print("removing duplicate mtl for " + os.path.join(os.path.split(obj_file_path)[0], rocketbox_character_name))
        remove_duplicate_mtl(os.path.join(os.path.split(obj_file_path)[0], rocketbox_character_name))

        set_empty_scene()
        reset_blend()


if __name__ == '__main__':
    main()

    # blender --python cleanup_scripts\combine_textures\rocketboxTPose.py
