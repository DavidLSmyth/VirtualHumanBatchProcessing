import os
import sys
import random

from utils.utils import get_relative_corresponding_output_file_name, get_export_file_name

sys.path.append(".")
from format_converters.ImportExportParamManager import ExportArgsManager, ImportArgsManager

from format_converters.converter import get_import_fn_args_dict, import_file, get_export_fn_args_dict, export_file, \
    can_convert, MeshFormatExporter
from scene_manager.scene_manager import reset_blend, deselect_all, get_start_animation_frame, get_end_animation_frame, \
    set_animation_frame, get_objects_by_type, delete_hierarchy
from animation_retargeting.API.retargeting import retarget_main

try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

def retarget_animation_file_to_mesh_file(import_armature_file_loc, import_animation_file_loc, animation_armature_name = None, mesh_armature_name = None, verbose = False):
    '''
    Retargets the animation in import_anim_file_loc to import_armature_file_loc. Doesn't export
    :param import_armature_file_loc: File location of the mesh file to retarget to. Should be .fbx format.
    :param import_animation_file_loc: File location of the animation file which will be retargeted to import_mesh_file_loc. Should be .fbx format.
    :param export_file_folder: Folder which the resulting retargeted animation will be saved.
    :param animation_armature_name: Name of the animation file armature. If None it will be auto-detected
    :param mesh_armature_name: Name of the mesh file armature. If None it will be auto-detected
    :return:
    '''

    reset_blend()
    #check file formats supported
    assert can_convert(import_animation_file_loc)
    assert can_convert(import_armature_file_loc)

    # load animation
    #file type excludes the '.' i.e use [1:]
    import_args_manager = ImportArgsManager(import_file_type=os.path.splitext(import_animation_file_loc)[1][1:])

    import_args_manager.set_import_arg("filepath", import_animation_file_loc)
    import_file(import_args_manager.get_import_args_dict(), verbose=verbose)
    animation_armature = get_objects_by_type("ARMATURE")[0]
    animation_armature_name = get_objects_by_type("ARMATURE")[0].name

    # load mesh & armature
    # file type excludes the '.' i.e use [1:]
    import_args_manager = ImportArgsManager(import_file_type=os.path.splitext(import_armature_file_loc)[1][1:])
    import_args_manager.set_import_arg("filepath", import_armature_file_loc)
    import_args_manager.set_import_arg("use_anim", False)
    import_file(import_args_manager.get_import_args_dict(), verbose=verbose)

    mesh_armature_name = get_objects_by_type("ARMATURE")[0].name if get_objects_by_type("ARMATURE")[0].name != animation_armature_name else get_objects_by_type("ARMATURE")[1].name
    mesh_armature = get_objects_by_type("ARMATURE")[0] if get_objects_by_type("ARMATURE")[0].name != animation_armature_name else get_objects_by_type("ARMATURE")[1]

    print(f"animation_armature_name: {animation_armature_name}, mesh_armature_name: {mesh_armature_name}")

    # retarget animation from source armature to target armature
    retarget_main(animation_armature_name, mesh_armature_name)

    # easier to remove animation object and then export remaining
    deselect_all()
    bpy.data.objects[animation_armature_name].select_set(True)
    delete_hierarchy(animation_armature.name)
    bpy.ops.object.delete()


def retarget_animation_file_and_export_mesh_frames(import_armature_file_loc, import_animation_file_loc, export_extension, export_folder_location, frame_list = [], export_args_manager = None, animation_armature_name=None, mesh_armature_name=None):
    '''
    Retargets an animtion and then exports individual frames.
    :param import_armature_file_loc: location of the armature/mesh file to import
    :param import_animation_file_loc: location of the animation file to import
    :param animation_armature_name: name of the animation that will be re-targeted
    :param mesh_armature_name: name of the armature that will be re-targeted to
    :param export_extension: the full extension of the destination. e.g. .obj
    :param export_folder_location: the destination folder to export to
    :param frame_list: list of frames to export
    :param export_args_manager: optionally can provide an export_args_manager. filepath will be overwritten but other args will be kept
    :return:
    '''

    retarget_animation_file_to_mesh_file(import_armature_file_loc, import_animation_file_loc, animation_armature_name, mesh_armature_name)
    if not export_args_manager:
        export_args_manager = ExportArgsManager(export_extension[1:])

    #sometimes obj doesn't export textures properly
    #as a hack, export textures using gltf
    if(export_extension == ".obj"):
        gltf_export_args_manager = ExportArgsManager("gltf")
        gltf_export_args_manager.set_export_arg("export_format", "GLTF_SEPARATE")

        export_args_manager.set_export_arg("path_mode", "STRIP")
        export_args_manager.set_export_arg("use_materials", True)
        export_args_manager.set_export_arg("use_normals", True)

    if not frame_list:
        frame_list = [index for index in range(get_start_animation_frame(), get_end_animation_frame())]

    for frame_index in frame_list:
        set_animation_frame(int(frame_index))
        export_file_name = get_export_file_name(export_extension, mesh_file_name=os.path.basename(import_armature_file_loc),
                                                export_frame=int(frame_index), animation_name=os.path.basename(import_animation_file_loc),
                                                separator='#', metadata_format_string=None)

        export_args_manager.set_export_arg("filepath", os.path.join(export_folder_location, export_file_name))
        export_file(export_args_manager.get_export_args_dict())

    #export gltf once for textures
    gltf_export_args_manager.set_export_arg("filepath", os.path.join(export_folder_location, "temp.gltf"))
    export_file(gltf_export_args_manager.get_export_args_dict())
    #remove gltf bin file and .gltf file
    os.remove(os.path.join(export_folder_location, "temp.gltf"))
    os.remove(os.path.join(export_folder_location, "temp.bin"))


def retarget_and_export_animation(import_armature_file_loc, import_animation_file_loc, export_extension, export_folder_location, export_file_name = None, start_frame = None, end_frame = None, export_args_manager = None,  animation_armature_name=None, mesh_armature_name=None):
    '''
    Exports the re-targeted animation as an fbx, bvh, gltf, obj
    :param export_folder_location: where to export the file
    :param start_frame: if None, the first frame of the imported animation
    :param end_frame:if None, the last frame of the imported animation
    :param export_extension: the full extension of the destination. e.g. .obj
    :return:
    '''

    retarget_animation_file_to_mesh_file(import_armature_file_loc, import_animation_file_loc, animation_armature_name, mesh_armature_name)

    if not export_args_manager:
        export_args_manager = ExportArgsManager(export_extension[1:])

    if not start_frame:
        start_frame = get_start_animation_frame()

    if not end_frame:
        end_frame = get_end_animation_frame()

    assert start_frame <= end_frame

    if export_extension == ".fbx":
        export_args_manager.set_export_arg("bake_anim", True)

    elif export_extension == ".obj":
        export_args_manager.set_export_arg("use_animation", True)

    elif export_extension == ".bvh":
        export_args_manager.set_export_arg("frame_start", start_frame)
        export_args_manager.set_export_arg("frame_end", end_frame)

    elif export_extension == ".gltf":
        export_args_manager.set_export_arg("export_animations", True)

    if not export_file_name:
        export_file_name = get_export_file_name(export_extension, mesh_file_name=os.path.basename(import_armature_file_loc),
                                                    export_start_frame = start_frame, export_end_frame = end_frame, animation_name=os.path.basename(import_animation_file_loc),
                                                    separator='#', metadata_format_string=None)
    export_args_manager.set_export_arg("filepath", os.path.join(export_folder_location, export_file_name))
    export_file(export_args_manager.get_export_args_dict())
    reset_blend()


def retarget_files_multiple_frames(import_armature_file_loc, import_anim_file_loc, export_file_folder, animation_armature_name, mesh_armature_name, start_frame=None, end_frame=None, verbose = False):
    '''
    :param import_armature_file_loc: File location of the mesh file to retarget to. Should be .fbx format.
    :param import_anim_file_loc: File location of the animation file which will be retargeted to import_mesh_file_loc. Should be .fbx format.
    :param export_file_folder: Folder which the resulting retargeted animation will be saved.
    :param animation_armature_name: Name of the animation file armature.
    :param mesh_armature_name: Name of the mesh file armature.
    :param start_frame: First frame of animation to retarget.
    :param end_frame: Last frame of animation to retarget.
    :return:
    '''

    retarget_animation_file_to_mesh_file(import_armature_file_loc, import_anim_file_loc, export_file_folder,
                                         animation_armature_name, mesh_armature_name)

    if not start_frame:
        start_frame = get_start_animation_frame()
    if not end_frame:
        end_frame = get_end_animation_frame()

    bpy.context.scene.frame_set(start_frame)

    separator = '#'

    export_file_loc = os.path.join(export_file_folder,  os.path.splitext(os.path.basename(import_armature_file_loc))[0] + separator + os.path.splitext(os.path.basename(import_anim_file_loc))[0] + separator + "start_frame{:03d}".format(start_frame) + separator + "end_frame{:03d}".format(end_frame) + ".fbx" )#r"D:\TCDFiles\3dGeom\SquatData\SquatMeshes\Female_Adult_01#air_squat.fbx"
    print("exporting to " + export_file_loc)
    export_args = get_export_fn_args_dict("fbx")
    export_args["filepath"] = export_file_loc
    export_args["object_types"] = {"ARMATURE", "MESH"}
    # export_args["use_selection"] = True
    export_args["embed_textures"] = True
    export_args["bake_anim"] = start_frame != end_frame
    print(export_args)
    export_file(export_file_loc, export_args, verbose=True)



def retarget_files_single_frame(import_mesh_file_loc,import_anim_file_loc, export_file_folder, frame_to_render, animation_armature_name, mesh_armature_name):
    '''
    Retargets the animation in import_anim_file_loc to import_mesh_file_loc for a given frame
    :param import_mesh_file_loc:
    :param import_anim_file_loc:
    :param export_file_folder:
    :param frame_to_render:
    :param animation_armature_name:
    :param mesh_armature_name:
    :return:
    '''

    retarget_files_multiple_frames(import_mesh_file_loc,import_anim_file_loc, export_file_folder, animation_armature_name, mesh_armature_name, start_frame = frame_to_render, end_frame = frame_to_render)

    
    


#def main():
#    mesh_names = os.listdir(r"D:\TCDFiles\3dGeom\SquatData\Mesh")

#    for mesh_name in mesh_names:
#        print("Retargeting ", mesh_name)
#        retarget_files(r"D:\TCDFiles\3dGeom\SquatData\Mesh\{mesh_name}\{mesh_name}.fbx".format(mesh_name=mesh_name),
#                   r"D:\TCDFiles\3dGeom\SquatData\Animation\FBX\air_squat.fbx",
#                   r"D:\TCDFiles\3dGeom\SquatData\SquatMeshes", 25)


#if __name__ == "__main__":
#    main()
