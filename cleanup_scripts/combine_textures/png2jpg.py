# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 15:17:51 2021

@author: admin
"""

from PIL import Image
import os

import re
import os


    

def png2jpg(png_img_loc, jpg_img_loc):
    im = Image.open(png_img_loc)
    rgb_im = im.convert('RGB')
    rgb_im.save(jpg_img_loc)
    
    
def update_mtl_jpg(mtl_file_loc, png_file_name, jpg_file_name):
    '''
    when converting from png to jpg, updates the material file to now read from png
    :param mtl_file_loc:
    :param png_file_name:
    :param jpg_file_name:
    :return:
    '''
    with open(mtl_file_loc, 'r+') as f:
        mtl_file_contents = f.read()
        print(png_file_name)
        mtl_file_contents = mtl_file_contents.replace(png_file_name, jpg_file_name)
        print("writing ", mtl_file_contents)
        f.seek(0)
        f.write(mtl_file_contents)
        f.truncate()
    
    
def main():
    #this assumes a flat file hierarchy, all files at same level
    for root, dirs, files in os.walk(r"D:\SAUCEFiles\MixamoCharacters\MixamoChars\unpackedTextures"):
        png = [file for file in files if file[-3:]=='png']
        #jpg = [file for file in files if file[-3:]=='jpg']
        mtl = [file for file in files if file[-3:]=='mtl']
        if len(png) != 1:
            continue
        #assert len(jpg) in [0,1]
        assert len(mtl) == 1
        

        print("converting png to jpg for ", os.path.join(root, png[0]))
        png2jpg(os.path.join(root, png[0]), os.path.join(root, png[0].replace("png", "jpg")))
        
        update_mtl_jpg(os.path.join(root, mtl[0]), png[0], png[0].replace("png", "jpg"))
            
main()