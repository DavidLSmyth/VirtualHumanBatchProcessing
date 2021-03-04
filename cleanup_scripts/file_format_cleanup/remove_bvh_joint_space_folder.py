import argparse
import os
import sys
sys.path.append("..")
sys.path.append(".")
from cleanup_scripts.file_format_cleanup.remove_bvh_joint_space_file import remove_joint_spaces_bvh

def get_args():
    argparser = argparse.ArgumentParser("Given a bvh file, replaces spaces in joint names with underscore")
    argparser.add_argument("bvh_folder", help = "Path to the bvh file")
    argparser.add_argument("--destination_folder", help = "Path to the destination file to save to. Exclude to overwrite bvh_file")
    args = argparser.parse_args()
    return args


def remove_joint_spaces_folder():
    args = get_args()
    assert os.path.exists(args.bvh_folder)
    bvh_folder = args.bvh_folder
    if not args.destination_folder:
        destination_folder = bvh_folder
    else:
        destination_folder = args.destination_folder

    for file in os.listdir(bvh_folder):
        remove_joint_spaces_bvh(os.path.join(bvh_folder, file), os.path.join(destination_folder, file))

def main():
    remove_joint_spaces_folder()
        #f.write('\n'.join(bvh_lines))

if __name__ == "__main__":
    main()

