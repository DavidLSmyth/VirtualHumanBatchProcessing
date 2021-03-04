import os


def remove_duplicate_mtl(obj_folder):
    '''
    Assumes that there are duplicate png & mtl files in the given folder with objs. This function deletes the duplicate png & mtl and edits the corresponding obj files
    :return:
    '''
    print(os.listdir(obj_folder))
    mtl_files = list(filter(lambda x: os.path.splitext(x)[1] == ".mtl", os.listdir(obj_folder)))
    obj_files = list(filter(lambda x: os.path.splitext(x)[1] == ".obj", os.listdir(obj_folder)))
    png_files = list(filter(lambda x: os.path.splitext(x)[1] == ".png", os.listdir(obj_folder)))

    print("obj_folder: ",obj_folder)
    print("mtl_files: ", mtl_files)
    print("obj_files: ", obj_files)
    print("png_files: ", png_files)

    png_to_keep = png_files[-1]
    mtl_to_keep = mtl_files[-1]

    for png_file in png_files[:-1]:
        os.remove(os.path.join(obj_folder, png_file))
    for mtl_file in mtl_files[:-1]:
        os.remove(os.path.join(obj_folder, mtl_file))

    #rename atlas to rocketbox character name
    rocketbox_char_name = os.path.split(obj_folder)[1]
    print("rocketbox_char_name: ", rocketbox_char_name)
    #png_base_path = os.path.basename(obj_folder)

    new_name = os.path.join(obj_folder, rocketbox_char_name + ".png")
    print("renaming {} to {}".format(os.path.join(obj_folder, png_to_keep), new_name))
    os.rename(os.path.join(obj_folder, png_to_keep), new_name)

    png2jpg(new_name, new_name.replace("png", "jpg"))

    update_mtl_file(os.path.join(obj_folder, mtl_to_keep), rocketbox_char_name)

    for obj_file in obj_files:
        update_obj_file(os.path.join(obj_folder, obj_file), rocketbox_char_name)



def update_mtl_file(mtl_file_loc, rocketbox_char_name):
    mtl_file_read = open(mtl_file_loc, 'r')
    text = mtl_file_read.read()

    updated_text = re.sub("material_atlas_[0-9]+", rocketbox_char_name, text)
    updated_text = re.sub("Atlas_[0-9]+", rocketbox_char_name, updated_text)
    updated_text = re.sub(".png", ".jpg", updated_text)

    mtl_file_read.close()

    mtl_file_edit = open(mtl_file_loc, 'w')
    mtl_file_edit.write(updated_text)
    mtl_file_edit.close()

    # rename png and mtl to rocketbox character name
    #rocketbox_char_name
    new_name = os.path.join(os.path.split(mtl_file_loc)[0], rocketbox_char_name + '.mtl')
    os.rename(mtl_file_loc, new_name)

def update_obj_file(obj_file_loc, rocketbox_char_name):
    '''
    png and mtl should have already been renamed to rocketbox character name
    :param obj_file_loc:
    :param rocketbox_char_name:
    :return:
    '''
    obj_file_read = open(obj_file_loc, 'r')
    text = obj_file_read.read()
    #mtllib Female_Adult_05#angry#frame037.mtl
    updated_text = re.sub("mtllib .*.mtl", "mtllib "+rocketbox_char_name + ".mtl", text)
    updated_text = re.sub("material_atlas_[0-9]+", rocketbox_char_name, updated_text)
    updated_text = re.sub("Atlas_[0-9]+", rocketbox_char_name , updated_text)
    obj_file_read.close()

    obj_file_edit = open(obj_file_loc, 'w')
    obj_file_edit.write(updated_text)
    obj_file_edit.close()