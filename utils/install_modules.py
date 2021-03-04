# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 12:15:38 2020

@author: admin
"""

import configparser
import os
import subprocess

def install_modules():
    '''Installs modules in blender's bundled python from requirements.txt'''
    install_pip()
    #get absolute path of requirements file
    requirements_file_loc = "{}\..\config\requirements.txt".format(os.path.dirname(os.path.abspath(__file__)))
    res = subprocess.run(get_python_loc() + " -m pip install -r {}/../config/requirements.txt".format(os.path.dirname(os.path.abspath(__file__))))
    assert res.returncode == 0, "Could not install modules in {}".format(requirements_file_loc)


def get_python_loc():
    assert os.path.exists("./config/pythonConfig.ini"), "Run this from teh top level of the module"
    parser = configparser.ConfigParser()
    parser.read_file(open("./config/pythonConfig.ini", 'r'))
    python_loc = parser["pythonConfig"]["blenderPythonFolderLocation"]
    return python_loc + r"\python"

def install_pip():
    res = subprocess.run(get_python_loc() + r" -m ensurepip")
    assert res.returncode == 0, "Error ensuring pip is installed"

if __name__ == '__main__':
    install_modules()