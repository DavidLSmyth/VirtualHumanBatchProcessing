

import sys, os

try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)

sys.path.append('.')
from utils.configure_paths import configure_paths
configure_paths()

from blender_arg_parser.blender_arg_parser import ArgumentParserForBlender


class BaseRetargetingArgParser:
    def __init__(self):
        self.description = "Use this script to retarget animations onto armatures/meshes. Each animation file wil be re-targeted onto each armature/mesh file"

        self.parser = ArgumentParserForBlender()
        self.parser.add_argument('--animation_files', type=str, nargs="+",
                            help='The animation file(s) that will be used to re-targeted.')

        self.parser.add_argument('--armature_files', type=str, nargs="+",
                            help='The location of the mesh/armature file(s) on which the animation will be re-targeted.')

        self.parser.add_argument('--export_file_format', type=str,
                                 help='The full extention of the file to export.')

        self.parser.add_argument("--no_cores", type=int, default=1,
                                 help="The number of cores over which to distribute the re-targeting. Be careful not to overload the CPU.")

        self.update_description(self.description)

    def get_parser(self):
        return self.parser

    def get_args_dict(self):
        return vars(self.parser.parse_args())

    def update_description(self, description):
        self.parser.description = description


class FullAnimationRegargetingArgParser(BaseRetargetingArgParser):
    def __init__(self):
        self.description = "Use this script to retarget animations onto armatures/meshes. Each animation file wil be re-targeted onto each armature/mesh file. The full animation will be re-targeted and exported as an animation"
        super().__init__()
        self.parser.add_argument("--output_file", type=str,
                            help='The location of the file that will be saved.')

        self.parser.add_argument("--output_folder", type=str,
                                 help='The location of the folder which the output file will be saved in. Use this when importing/exporting multiples files. Ignored if output_file provided also')


class FrameRangeAnimationRegargetingArgParser(FullAnimationRegargetingArgParser):
    def __init__(self):
        self.description = "Use this script to retarget animations onto armatures/meshes. Each animation file wil be re-targeted onto each armature/mesh file. Only the frame range will be re-targeted and exported as an animation"
        super().__init__()
        self.parser.add_argument("--start_frame", type=int,
                                 help='The first frame of the range to export')

        self.parser.add_argument("--end_frame", type=int,
                                 help='The last frame of the range to export')


class IndividualFramesAnimationRegargetingArgParser(FullAnimationRegargetingArgParser):
    def __init__(self):
        self.description = "Use this script to retarget animations onto armatures/meshes. Each animation file wil be re-targeted onto each armature/mesh file. Only the listed frames will be re-targeted and exported."
        super().__init__()
        self.parser.add_argument("--frames", type=str, nargs="+",
                                 help='The individual frames that will be exported')





