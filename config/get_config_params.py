import configparser



class GetDefaultConfigParams:

    config_file_loc = "./config/config.ini"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read_file(GetDefaultConfigParams.config_file_loc)

    def get_rocketbox_A_pose_adults_dir(self):
        return self.config["RocketboxAPoseConfig"]["AdultsFolderLocation"]

    def get_rocketbox_A_pose_children_dir(self):
        return self.config["RocketboxAPoseConfig"]["ChildrenFolderLocation"]

    def get_rocketbox_A_pose_professions_dir(self):
        return self.config["RocketboxAPoseConfig"]["ProfessionsFolderLocation"]

    def get_rocketbox_T_pose_adults_dir(self):
        return self.config["RocketboxTPoseConfig"]["AdultsFolderLocation"]

    def get_rocketbox_T_pose_children_dir(self):
        return self.config["RocketboxTPoseConfig"]["ChildrenFolderLocation"]

    def get_rocketbox_T_pose_professions_dir(self):
        return self.config["RocketboxTPoseConfig"]["ProfessionsFolderLocation"]

    def get_mixamo_animation_dir(self):
        return self.config["MixamoAnimations"]["AnimationsFolderLocation"]

    def get_mixamo_character_dir(self):
        return self.config["MixamoAnimations"]["AnimationsFolderLocation"]





