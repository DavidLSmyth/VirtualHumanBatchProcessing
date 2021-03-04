import argparse
import sys
import time
import random
import os
sys.path.append(".")
from example_scripts.retarget_animation_and_export_mesh import retarget_files_single_frame

def get_cmd_line_args():
    argv = sys.argv
    print("argv before processing: ", argv)
    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"
    return argv

def get_arg_parser():
    usage_text = ('''Run me''')
    parser = argparse.ArgumentParser(description=usage_text)
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-import_files",
                        type = str)
    argparser.add_argument("-export_folder_loc",
                        type=str)
    argparser.add_argument("-frame_no", 
                           type = int)
    argparser.add_argument("-animation_file_loc",
                           type=str)
    argparser.add_argument("-animation_armature_name",
                           type = str)
    argparser.add_argument("-mesh_armature_name",
                           type=str)
    
    return argparser



def main():
    argparser = get_arg_parser()

    print("running ")
    argv = get_cmd_line_args()
    print("argv: ", argv)
    args = vars(argparser.parse_known_args(argv)[0])
    print("read args: ", args)
    mesh_names = args["import_files"].split(' ')
        #os.listdir(args["import_folder_loc"])

    for mesh_name in mesh_names:
        print("Retargeting ", mesh_name)
        retarget_files_single_frame(mesh_name, args["animation_file_loc"],
                        args["export_folder_loc"], args["frame_no"],
                       args["animation_armature_name"], args["mesh_armature_name"])

        
   #time.sleep(random.random() * 2)
    #argparser.parse_args([next_line])


if __name__ == "__main__":
    main()