# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 13:01:30 2020

@author: admin
"""

import os
import sys
from typing import *
import inspect
import re
from collections import namedtuple


try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

sys.path.append('.')
from utils.configure_paths import configure_paths

configure_paths()

from scene_manager.scene_manager import set_empty_scene


conversion_types = {"mesh": ["ply", "stl"],
                    "scene": ["fbx", "obj", "gltf", "x3d"],
                    "anim": ["bvh"],
                    "wm": ["abc", "dae", "usd"]
                    }

#format these with either import or export
#this dict contains the mapping from file type to import/export function. Add to this in order to extend functionality
import_export_fn_mappings = {"abc" : "bpy.ops.wm.alembic_{}",
                    "dae" : "bpy.ops.wm.collada_{}",
                    #usd is export only
                    "usd" : "bpy.ops.wm.usd_{}",
                   "ply" : "bpy.ops.{}_mesh.ply",
                   "stl" : "bpy.ops.{}_mesh.stl",
                   "fbx" : "bpy.ops.{}_scene.fbx",
                   "obj" : "bpy.ops.{}_scene.obj",
                   "gltf" : "bpy.ops.{}_scene.gltf",
                   "x3d" : "bpy.ops.{}_scene.x3d",
                   "bvh" : "bpy.ops.{}_anim.bvh"
                   }

valid_formats = list(import_export_fn_mappings.keys())





#def import_fbx(filepath='', directory='', filter_glob='*.fbx', files=None, ui_tab='MAIN', use_manual_orientation=False, global_scale=1.0, bake_space_transform=False, use_custom_normals=True, use_image_search=True, use_alpha_decals=False, decal_offset=0.0, use_anim=True, anim_offset=1.0, use_subsurf=False, use_custom_props=True, use_custom_props_enum_as_string=True, ignore_leaf_bones=False, force_connect_children=False, automatic_bone_orientation=False, primary_bone_axis='Y', secondary_bone_axis='X', use_prepost_rot=True, axis_forward='-Z', axis_up='Y')

def is_valid_conversion_format(file_format):
    return file_format in import_export_fn_mappings


def assert_is_valid_conversion_format(file_format):
    assert is_valid_conversion_format(file_format), "Please provide a file format in the list {}".format(list(import_export_fn_mappings.keys()))


def get_import_fn_name(file_format: str) -> str:
    assert is_valid_conversion_format(file_format), "Please provide a file format in the list {}".format(list(import_export_fn_mappings.keys()))
    return import_export_fn_mappings[file_format].format("import")

def get_import_fn(file_format: str) -> Callable:
    return eval(get_import_fn_name(file_format))


def get_import_fn_args_string(file_format: str) -> str:
    return re.findall("\((.*)\)", get_import_fn(file_format)._get_doc())[0]


def get_export_fn_args_string(file_format: str) -> str:

    return re.findall("\((.*)\)", get_export_fn(file_format)._get_doc())[0]

    #return inspect.signature(get_export_fn(file_format))


def __get_args_dict_from_string(args_string):
    try:
        args_dict = dict(key_val_pair.split('=') for key_val_pair in args_string.split(', '))
    except Exception as e:
        print("args string: ",args_string)
        raise e
    for key, value in args_dict.items():
        args_dict[key] = eval(value)
    return args_dict

def get_export_fn_args_dict(file_format:str) -> dict:
    assert_is_valid_conversion_format(file_format)
    if file_format == "fbx":
        return {"filepath": '', "check_existing": True, "filter_glob": "*.fbx", "use_selection": False
            , "use_active_collection": False
            , "global_scale": 1
            , "apply_unit_scale": True
            , "apply_scale_options": 'FBX_SCALE_NONE'
            , "bake_space_transform": False
            , "object_types": {'EMPTY', 'CAMERA', 'LIGHT', 'ARMATURE', 'MESH', 'OTHER'}
            , "use_mesh_modifiers": True
            , "use_mesh_modifiers_render": True
            , "mesh_smooth_type": 'OFF'
            , "use_subsurf": False
            , "use_mesh_edges": False
            , "use_tspace": False
            , "use_custom_props": False
            , "add_leaf_bones": True
            , "primary_bone_axis": 'Y'
            , "secondary_bone_axis": 'X'
            , "use_armature_deform_only": False
            , "armature_nodetype": 'NULL'
            , "bake_anim": True
            , "bake_anim_use_all_bones": True
            , "bake_anim_use_nla_strips": True
            , "bake_anim_use_all_actions": True
            , "bake_anim_force_startend_keying": True
            , "bake_anim_step": 1
            , "bake_anim_simplify_factor": 1
            , "path_mode": 'AUTO'
            , "embed_textures": False
            , "batch_mode": 'OFF'
            , "use_batch_own_dir": True
            , "use_metadata": True
            , "axis_forward": '-Z'
            , "axis_up": 'Y'}
    else:
        return __get_args_dict_from_string(get_export_fn_args_string(file_format))

def get_import_fn_args_dict(file_format:str) -> dict:
    assert_is_valid_conversion_format(file_format)
    return __get_args_dict_from_string(get_import_fn_args_string(file_format))



def get_export_fn_name(file_format: str) -> str:
    assert is_valid_conversion_format(file_format), "Please provide a file format in the list {}".format(list(import_export_fn_mappings.keys()))
    return import_export_fn_mappings[file_format].format("export")



def get_export_fn(file_format: str) -> Callable:
    return eval(get_export_fn_name(file_format))


def __export_file(kwargs, verbose = False):
    '''Imports a file into the active blender scene based on the input_file_loc extension with the provided args and kwargs'''
    #print("Executing: {fn}(*{args}, **{kwargs})".format(fn = import_export_fn_mappings[get_file_ext(export_file_loc)].format("export"), args = args, kwargs = kwargs))

    export_fn = get_export_fn(get_file_ext(kwargs["filepath"]))
    if verbose:
        print("Executing: {fn_name}(**{kwargs})".format(fn_name = str(export_fn), kwargs = kwargs))
    export_fn(**kwargs)
    #exec("{fn}(*{args}, **{kwargs})".format(fn = import_export_fn_mappings[get_file_ext(export_file_loc)].format("export"), args = args, kwargs = kwargs))

def __import_file(kwargs, verbose = False):
    '''Imports a file into the active blender scene based on the input_file_loc extension with the provided args and kwargs'''
    import_fn = get_import_fn(get_file_ext(kwargs["filepath"]))
    if verbose:
        print("Executing: ", "{fn_name}(**{kwargs})".format(fn_name = str(import_fn), kwargs = kwargs))
    import_fn(**kwargs)
    #exec("{fn}(*{args}, **{kwargs})".format(fn = import_export_fn_mappings[get_file_ext(input_file_loc)].format("import"), args = args, kwargs = kwargs))

def __convert(import_kwargs: dict, export_kwargs: dict, clear_scene = True):
    __import_file(import_kwargs)
    __export_file(export_kwargs)
    if clear_scene:
        set_empty_scene()


def get_file_ext(file_path: str) -> str:
    #print("file_name: ", file_name)
    return os.path.splitext(file_path)[1][1:]

def get_folder(file_path):
    return os.path.split(file_path)[0]

def can_convert(file_name: str) -> str:
    return get_file_ext(file_name) in valid_formats

def convert_args_manager(import_args_manager: "ImportArgsManager", export_args_manager: "ExportArgsManager", create_export_path = False):
    '''
    Converts a file read in specified by import_args_manager to a file specified by export_args_manager
    :param import_args_manager:
    :param export_args_manager:
    :return:
    '''
    convert(import_args_manager.get_import_args_dict(), export_args_manager.get_export_args_dict(), create_export_path)

def convert(import_kwargs: dict, export_kwargs: dict, create_export_path = False):
    import_file = import_kwargs["filepath"]
    export_file = export_kwargs["filepath"]

    if create_export_path:
        if not os.path.isdir(os.path.dirname(export_file)):
            os.mkdir(os.path.dirname(export_file))

    assert os.path.exists(import_file), "{} is not a valid file location".format(import_file)
    assert os.path.exists(os.path.dirname(export_file)), "{} is not a valid file location".format(export_file)
    assert can_convert(import_file), get_file_ext(import_file) + " files are not supported"
    assert can_convert(export_file), get_file_ext(export_file) + " files are not supported"
    __convert(import_kwargs, export_kwargs)

def export_file(kwargs, verbose = False):
    export_file_loc = kwargs["filepath"]
    folder_path = os.path.dirname(export_file_loc)
    assert os.path.exists(folder_path), "{} is not a valid export location, it doesn't exist".format(folder_path)
    assert can_convert(export_file_loc), get_file_ext(export_file_loc) + " files are not supported"
    __export_file(kwargs, verbose)

def import_file(kwargs, verbose = False):
    import_file_loc = kwargs["filepath"]
    assert os.path.exists(import_file_loc), "{} is not a valid file location".format(import_file_loc)
    assert can_convert(import_file_loc), get_file_ext(import_file_loc) + " files are not supported"
    __import_file(kwargs, verbose)

def get_conversion_function(file_type: str, import_or_export: str = "import") -> Callable:
    '''
    Returns a function to import/export the given file_typ
    '''
    if file_type in import_export_fn_mappings:
        return eval(import_export_fn_mappings[file_type].format(import_or_export))
    else:
        raise NotImplementedError("Cannot {import_or_export} to/from a {file_type} file".format(import_or_export = import_or_export, file_type = file_type))

class BaseFormatExporter():

    def __init__(self, export_type):
        assert export_type in conversion_types
        self.export_type = export_type

    def export(self):
        '''Overridden in subclasses'''
        pass

    def select_objects_by_type(self, object_type: str, scene = None):
        bpy.ops.object.select_all(action='DESELECT')

        for scene_object in self.get_objects_by_type(object_type, scene):
            scene_object.select = True

    def get_objects_by_type(self, object_type: str, scene = None) -> List:
        return_objects = []

        if not scene:
            #assume using the open scene
            scene = bpy.context.scene

        for ob in scene.objects:
            # make the current object active and select it
            #scene.objects.active = ob
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob

            # make sure that we only export meshes
            if ob.type == object_type:
                return_objects.append(ob)
        return return_objects

class SceneFormatExporter(BaseFormatExporter):
    '''
    Wrapper around the blender mesh export operators. Refer to https://docs.blender.org/api/current/bpy.ops.export_scene.html for details of args and kwargs to be used with each format type.
    '''
    #use this to only select  in the open scene
    def __init__(self):
        super().__init__("scene")

    def export_scene(self, file_name, kwargs = dict(), verbose = False):
        '''
        Exports a to scene file with the given kwargs. Args and kwargs vary depending
        on the export format, look up docs for details.
        '''
        #assume everything should be exported
        #if not object_types:
        #    object_types = {'EMPTY', 'CAMERA', 'LIGHT', 'ARMATURE', 'MESH', 'OTHER'}


        export_file(file_name,  kwargs, verbose)





class MeshFormatExporter(BaseFormatExporter):
    '''
    Wrapper around the blender mesh export operators. Refer to https://docs.blender.org/api/current/bpy.ops.export_mesh.html for details of args and kwargs to be used with each format type.
    '''
    #use this to only select meshes in the open scene
    object_type = "MESH"

    def __init__(self):
        super().__init__("mesh")

    def export_individual_meshes(self, output_folder_name, export_type, kwargs, scene = None):
        '''Exports each mesh in the scene to an individual file'''
        assert export_type in valid_formats
        meshes = super().get_objects_by_type(MeshFormatExporter.object_type, scene)
        for mesh in meshes:
            mesh.select_set(True)
            #save in output format
            print("saving " + mesh.name)
            #output_file_name = output_folder_name + "/{}".format(mesh.name) + "." + export_type
            #kwargs = {"filepath" : output_file_name, "use_selection" : True}

            export_file(output_file_name, kwargs)
            mesh.select_set(False)

    def export_all_meshes(self, output_file_name, export_type, kwargs: dict, scene = None):
        '''Exports all meshes in the scene to single file composed of the meshes'''
        meshes = super().get_objects_by_type(MeshFormatExporter.object_type, scene)
        for mesh in meshes:
            mesh.select_set(True)
        export_file(output_file_name, kwargs)

    def export(self, export_args_manager):
        export_file(export_args_manager.get_export_args_dict())





class AnimFormatExporter(BaseFormatExporter):
    #use this to only select animations in the open scene
    '''
    Wrapper around the blender mesh export operators. Refer to https://docs.blender.org/api/current/bpy.ops.export_anim.html for details of args and kwargs to be used with each format type.
    '''

    def __init__(self):
        super().__init__("anim")

    def export_all_animations(output_folder_name):
        pass

    def export_selected_animation(output_file_name, kwargs = dict()):
        kwargs["filepath"] = output_file_name
        export_file(output_file_name, args, kwargs)



class WmFormatExporter(BaseFormatExporter):
    def __init__(self):
        super().__init__("wm")





if __name__ == '__main__':

    set_empty_scene(True)
    cmu_import_file_name = "01_01"
    import_file_loc = r"D:\SAUCEFiles\MotionDatabase\Database\BVH\{}.bvh".format(cmu_import_file_name)

    import_args = get_import_fn_args_dict("bvh")

    import_args["filepath"] = import_file_loc

    import_file(import_file_loc, import_args, verbose = True)

    bpy.ops.object.mode_set(mode = "POSE")
    bpy.ops.pose.armature_apply(selected = False)

    fa_import_file_name = "loc_0004"

    import_file_loc = r"D:\SAUCEFiles\MotionDatabase\Database\BVH\{}.bvh".format(fa_import_file_name)
    import_args["filepath"] = import_file_loc
    import_file(import_file_loc, import_args, verbose = True)

    #rescale so source matches target
    bpy.context.selected_objects[0].scale[0] = 0.2
    bpy.context.selected_objects[0].scale[1] = 0.2
    bpy.context.selected_objects[0].scale[2] = 0.2

    #bpy.data.objects['Cube'].select_set(True)

    #bpy.data.objects[fa_import_file_name].select_set(True)
    bpy.data.scenes["Scene"].rsl_retargeting_armature_source = bpy.data.objects[fa_import_file_name]
    bpy.data.scenes["Scene"].rsl_retargeting_armature_target = bpy.data.objects[cmu_import_file_name]

    print("available ops: ", dir(bpy.ops.rsl.import_custom_schemes))

    #load_custom_lists_from_file(r"C:/users/admin/Downloads/FAToCMU.json")
    #bpy.ops.rsl.import_custom_schemes.directory = r"C:/users/admin/Downloads/"
    #files = bpy.types.OperatorFileListElement('INVOKE_DEFAULT')
    #bpy.ops.rsl.import_custom_schemes( directory = r"C:/users/admin/Downloads/FAToCMU.json")
    bpy.ops.rsl.build_bone_list()
    bpy.ops.rsl.retarget_animation()

    bpy.data.objects[cmu_import_file_name].select_set(True)

    export_template = r"C:/users/admin/Downloads/{}.bvh"
    export_file_name = "test_retarget_export"
    export_args = get_export_fn_args_dict("bvh")
    export_args["filepath"] = export_template.format(export_file_name)
    export_args["root_transform_only"] = True
    export_file(export_template.format(export_file_name), export_args)

    set_empty_scene(True)

    #re-import file with correct orientations
    import_args["filepath"] = export_template.format(export_file_name)
    import_args["axis_forward"] = "Z"
    import_args["axis_up"] = "X"
    import_file(export_template.format(export_file_name), import_args)

    export_args["rotate_mode"] = "ZYX"
    export_file(export_template.format(export_file_name), export_args)

    #set hips offset to zero
    #bpy.data.armatures[export_]

    #print(get_import_fn_args_string("fbx"))
    #print(get_import_fn_args_dict("stl"))

    '''
    import_args = tuple()
    import_kwargs = {"filepath": import_file_loc}
    import_file(import_file_loc, import_args, import_kwargs)
    print("file imported")
    
    #remove_default_cube()
    #remove_default_camera()
    #remove_default_light()
    exporter = MeshFormatExporter()
    exporter.export_individual_meshes(r"data\test_output", "stl")
    print("file exported")
    
        '''






