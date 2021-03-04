# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 11:21:43 2020

@author: admin
Responsible for importing relevant modules, use in local scripts
"""

import sys
import os

def configure_paths():
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "..")
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "../utils")
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "../blender_cli_rendering")
    #sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../scripts/blender_cli_rendering_master")
        #import blender_cli_rendering_master.utils as utils
