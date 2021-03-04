import sys

sys.path.append(".")
from animation_retargeting.animation_regargeting_api import retarget_and_export_animation
from animation_retargeting.animation_retargeting_api_cmd_line import FullAnimationRegargetingArgParser

def get_args_list(armature_files, animation_files, output_folder, export_file_format):
    if len(armature_files) > 1:
        armature_files = armature_files.split(' ')
    if len(animation_files) > 1:
        animation_files = animation_files.split(' ')
    # create a list of command line args to process to be divided according to the number of cores
    args_to_proccess = [[armature_file, animation_file, export_file_format, output_folder] for armature_file, animation_file
                        in zip(animation_files, armature_files)]
    return args_to_proccess

def main():
    #returns a list of lists, each containing args to be executed by the retarget_and_export_animation function
    parser = FullAnimationRegargetingArgParser()
    args = vars(parser.get_parser().parse_args())
    print("Read args: ", args)
    armature_files = args["armature_files"]
    animation_files = args["animation_files"]
    output_folder = args["output_folder"]
    export_file_format = args["export_file_format"]
    args_list = get_args_list(armature_files, animation_files, output_folder, export_file_format)
    for args in args_list:
        retarget_and_export_animation(*args)


'''
def main():
    argparser = get_arg_parser()

    print("running ")
    argv = get_cmd_line_args()
    print("argv: ", argv)
    args = vars(argparser.parse_known_args(argv)[0])
    print("read args: ", args)
    mesh_names = args["import_files"].split(' ')
    # os.listdir(args["import_folder_loc"])

    for mesh_name in mesh_names:
        print("Retargeting ", mesh_name)
        #import_mesh_file_loc,import_anim_file_loc, export_file_folder, animation_armature_name, mesh_armature_name, start_frame = None, end_frame = None
        retarget_files_multiple_frames(mesh_name, args["animation_file_loc"], args["export_folder_loc"],
                                    args["animation_armature_name"], args["mesh_armature_name"], args["start_frame"], args["end_frame"])

'''
# time.sleep(random.random() * 2)
# argparser.parse_args([next_line])


if __name__ == "__main__":
    main()