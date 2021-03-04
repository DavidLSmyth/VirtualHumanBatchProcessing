
import sys
import math

from example_scripts.animation_retargeting.retarget_all_frames.retarget_animation_cmd_line import get_args_list
from multiprocessing.multiprocess import run_multiprocessed

sys.path.append(".")
from animation_retargeting.animation_regargeting_api import retarget_and_export_animation
from animation_retargeting.animation_retargeting_api_cmd_line import FullAnimationRegargetingArgParser

def get_args_partition(args_to_process, no_cores):
    no_args_per_partition = math.ceil(len(args_to_process) / no_cores)
    # partition the args to process to run on individual cores
    args_partitions = [args_to_process[core_index * no_args_per_partition: core_index * no_args_per_partition + no_args_per_partition]
        for core_index in range(no_cores)]
    return args_partitions


def get_args_list_multiprocessed(armature_files, animation_files):
    if len(armature_files) > 1:
        armature_files = armature_files.split(' ')
    if len(animation_files) > 1:
        animation_files = animation_files.split(' ')
    # create a list of command line args to process to be divided according to the number of cores
    args_to_proccess = [[armature_file, animation_file] for armature_file, animation_file
                        in zip(animation_files, armature_files)]



    return args_to_proccess

def main():
    # create a list of command line args to process to be divided according to the number of cores

    parser = FullAnimationRegargetingArgParser()
    args = vars(parser.get_parser().parse_args())
    print("Read args: ", args)
    armature_files = args["armature_files"]
    animation_files = args["animation_files"]
    output_folder = args["output_folder"]
    export_file_format = args["export_file_format"]
    no_cores = args["no_cores"]
    args_list = get_args_list_multiprocessed(armature_files, animation_files, )
    args_to_process = get_args_partition(args_list, args["no_cores"])

    # if input("using mesh_partitions: {}. Proceed?".format(mesh_partitions)) == 'n':
    #    sys.exit()
    for core_index in no_cores:
        for arg_list in args_to_process[core_index]:
            #self.parser.add_argument('animation_files', type=str, nargs="+",
        #                    help='The animation file(s) that will be used to re-targeted.')

        #self.parser.add_argument('armature_files', type=str, nargs="+",
        #                    help='The location of the mesh/armature file(s) on which the animation will be re-targeted.')

        #self.parser.add_argument('export_file_format', type=str,


            run_multiprocessed([["blender", "-b", "--python",
                         r"example_scripts/animation_retargeting/retarget_all_frames/retarget_animation_cmd_line.py",
                         "--", "--animation_files", ' '.join(next_to_retarget[0]),
                         "--armature_files ", ' '.join(next_to_retarget[1]),
                         "--output_folder", output_folder]
                        for next_to_retarget in arg_list])

if __name__ == "__main__":
    main()