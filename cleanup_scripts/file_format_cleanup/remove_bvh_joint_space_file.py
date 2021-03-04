import argparse
import os
import sys

def get_bvh_lines(bvh_file):
    with open(bvh_file, "r") as f:
        return f.readlines()

def replace_spaces(bvh_lines):
    for index, line in enumerate(bvh_lines):
        if "JOINT" in line:
            replacement = line.split("JOINT ")[1].replace(" ", "_")
            bvh_lines[index] = "JOINT " + replacement
    return bvh_lines

def get_args():
    argparser = argparse.ArgumentParser("Given a bvh file, replaces spaces in joint names with underscore")
    argparser.add_argument("bvh_file", help = "Path to the bvh file")
    argparser.add_argument("--destination_file", help = "Path to the destination file to save to. Exclude to overwrite bvh_file")
    args = argparser.parse_args()
    return args

def remove_joint_spaces_bvh(bvh_file, destination_file = None):

    assert os.path.splitext(bvh_file)[1] == '.bvh', "please provide a .bvh file, not {}".format(
        os.path.splitext(bvh_file)[1])
    if destination_file:
        destination_file = destination_file
        assert os.path.splitext(destination_file)[1] == '.bvh', "please provide a .bvh file, not {}".format(
            os.path.splitext(destination_file)[1])
    else:
        destination_file = bvh_file

    bvh_lines = get_bvh_lines(bvh_file)
    bvh_lines = replace_spaces(bvh_lines)
    with open(destination_file, "w") as f:
        f.writelines(bvh_lines)

def main():
    args = get_args()
    remove_joint_spaces_bvh(args.bvh_file, args.destination_file)
        #f.write('\n'.join(bvh_lines))

if __name__ == "__main__":
    main()