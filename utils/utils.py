import os

#useful as a decorator for conversion files
def apply_to_folder(func, input_folder_path, output_folder_loc, output_file_format, input_file_filter_function, recursive_search = False, import_kwargs = {}, export_kwargs = {}, verbose = False):
    '''
    :param func: Function to be applied to all files in a folder
    :param folder_path: Path to the folder for which files that pass the file_filter will run through func
    :param file_filter: A binary filter for file paths
    :return:
    '''
    assert os.path.exists(input_folder_path), f"{input_folder_path} is not a valid path on the file system"
    print([i for i in directory_iterator(input_folder_path, recursive_search, input_file_filter_function)])
    for input_file in directory_iterator(input_folder_path, recursive_search, input_file_filter_function):
        file_name, ext = os.path.splitext(input_file)
        output_file_path = os.path.join(output_folder_loc, file_name + f".{output_file_format}")
        input_file_path = os.path.join(input_folder_path, input_file)
        if verbose:
            print(f"Converting {input_file_path} to {output_file_path}")
        func(input_file_path, output_file_path)



def directory_iterator(directory, recursive = True, file_filter = None):
    '''
    Recursively searches directory for files matching filter
    :param directory: directory to iterate over
    :param recursive: whether to search recursively
    :param filter: the filter to apply
    :return: an iterator of file paths
    '''
    #file filter returns everything by default
    if not file_filter:
        file_filter = lambda x: True
    if recursive:
        for subdir, dirs, files in os.walk(directory):
            for file in filter(lambda file_name: file_filter(file_name), files):
                yield os.path.join(os.path.relpath(subdir,start = directory), file)
    else:
        for file in filter(lambda file_name: file_filter(file_name), os.listdir(directory)):
            yield os.path.join(directory, file)


def get_export_file_name(export_extension, mesh_file_name=None,
                                                export_start_frame=None, export_end_frame=None, export_frame=None, animation_name=None,
                                                separator='#', metadata_format_string=None):
    '''
    For args provided with a separator, returns corresponding file name
    :return:
    '''
    # use default if doesn't exist
    if not metadata_format_string:
        metadata_format_string = {"mesh_file_name": "mesh_name={}", "animation_name": "animation={}",
                                  "export_start_frame": "start_frame={:04d}", "export_end_frame": "end_frame={:04d}", "export_frame": "{:04d}"}

    # can't use comprehension due to eval scoping rules
    metadata_format_string_populated = {}
    for key, value in metadata_format_string.items():
        if eval(key):
            metadata_format_string_populated[key] = value.format(eval(key))
    # metadata_format_string_populated = {key: value for key, value in metadata_format_string.items() if eval(key) }
    file_name_with_metadata = separator.join(sorted(list(metadata_format_string_populated.values()))) + export_extension
    return file_name_with_metadata


def get_relative_corresponding_output_file_name(relative_import_folder, export_extension, mesh_file_name=None,
                                                export_start_frame=None, export_end_frame=None, animation_name=None,
                                                separator='#', metadata_format_string=None):
    '''
    For a given import file location, gives the relative export location (useful for keeping the same file structure but converting format)
    :param relative_import_folder: The relative folder location where the file was imported from
    :param export_extension: full file extension e.g. .obj
    :param mesh_file_name: the file name without extension for the mesh to export
    :param export_start_frame:
    :param export_end_frame:
    :param export_animation:
    :param separator:
    :return: relative files path with export name
    '''
    return os.path.join(relative_import_folder, get_export_file_name(export_extension, mesh_file_name=mesh_file_name,
                                                export_start_frame=export_start_frame, export_end_frame=export_end_frame, animation_name=animation_name,
                                                separator=separator, metadata_format_string=metadata_format_string))



