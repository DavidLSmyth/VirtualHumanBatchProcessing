import argparse
import os
import sys
sys.path.append("..")
sys.path.append(".")
from Multiprocessing.multiprocess import run_multiprocessed


def get_arg_parser():
    parser = argparse.ArgumentParser(description='Convert a folder of fbx to bvh')

    parser.add_argument('-bvh_folder',  type=str,
                        help='The folder containing the bvh files to convert.')

    parser.add_argument('-csv_folder', type = str,
                        help = 'The folder containing the converted csv files.')
    return parser

def bvh2csv(bvh_file_path, csv_file_path):
    '''
    Converts a bvh file to a world pos csv file
    :return:
    '''
    print("Running", getbvh2csv_args(bvh_file_path, csv_file_path))
    #os.system(" ".join([r"RScript.exe", r"C:\Users\admin\3DGeom\blender3dgscripts\format_converters\bvh_to_csv.R", bvh_file_path, csv_file_path]))
    os.system(getbvh2csv_args(bvh_file_path, csv_file_path))

def getbvh2csv_args(bvh_file_path, csv_file_path):
    return " ".join([r'"C:\Program Files\R\R-4.0.3\bin\x64\RScript.exe"', r"C:\Users\admin\3DGeom\blender3dgscripts\format_converters\bvh_to_csv.R", "-i", bvh_file_path, "-o" ,csv_file_path])


def bvh_folder2csv_multiprocessed(bvh_folder, csv_folder):
    args =  []
    for file in os.listdir(bvh_folder):
        args.append(getbvh2csv_args(os.path.join(bvh_folder, file), os.path.join(csv_folder, os.path.splitext(file)[0] + ".csv")))
    run_multiprocessed(args)

def bvh_folder2csv(bvh_folder, csv_folder):
    print("Make sure RScript is on the path!")

    for file in os.listdir(bvh_folder):
        bvh2csv(os.path.join(bvh_folder, file), os.path.join(csv_folder, os.path.splitext(file)[0] + ".csv"))

if __name__ == "__main__":
    bvh_folder2csv(r"D:\TCDFiles\3dGeom\SquatData\SquatMeshes\bvh_no_space", r"D:\TCDFiles\3dGeom\SquatData\SquatMeshes\csv_world_pos_R_mocap")
    #bvh_folder2csv_multiprocessed(r"D:\TCDFiles\3dGeom\SquatData\SquatMeshes\bvh_no_space", r"D:\TCDFiles\3dGeom\SquatData\SquatMeshes\csv_world_pos")