# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 16:56:23 2020

@author: admin
"""

import argparse
import os
import sys
from typing import *
from inspect import signature


try:
    import bpy
except ImportError:
    print("Module 'bpy' could not be imported. This probably means you are not using Blender to run this script.")
    sys.exit(1)


from format_converters.converter import get_import_fn_args_dict, get_export_fn_args_dict, valid_formats

from utils.configure_paths import configure_paths
configure_paths()

def get_cmd_line_args():
    argv = sys.argv	
    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"
    return argv



class ImportExportArgManager:
    '''
    An argument manager for the import and export of files. Automated param checking occurs depending on the file type
    '''
    def __init__(self, import_file_type: str = '', export_file_type: str = '', should_import_file: bool = False, should_export_file: bool = False):
        usage_text = ('''Use this tool to import/export files to blender. Supported formats: {}''').format(valid_formats)
        self.parser = argparse.ArgumentParser(description=usage_text)
        

        self.should_import_file = should_import_file
        self.should_export_file = should_export_file
        
        if self.should_import_file:
            assert import_file_type in valid_formats, f"Please provide a valid import file type from the list {valid_formats}, not {import_file_type}"
        if self.should_export_file:
            assert export_file_type in valid_formats, f"Please provide a valid export file type from the list {valid_formats}, not {export_file_type}"
        
        self.import_file_type = import_file_type
        self.export_file_type = export_file_type
        
        #these should not be directly exposed to the user since valid params depend on the file type
        self.__import_args = {}
        self.__export_args = {}
        self.__possible_import_args = get_import_fn_args_dict(self.import_file_type) if self.should_import_file else None
        self.__possible_export_args = get_export_fn_args_dict(self.export_file_type) if self.should_export_file else None
        
    def reset_args(self):
        '''
        Resets all available args to their defaults
        '''
        self.__import_args = self.__possible_export_args().copy()
        self.__export_args = self.__possible_export_args().copy()
        
    def get_available_args(self):
        '''
        For the given import and export file types, lists the available args for each.
        '''
        return {"available_import_args": self.__possible_import_args, "available_export_args": self.__possible_export_args}
        
    def set_import_arg(self, key, value):
        '''
        Sets/updates an import arguments value.
        '''
        if self.should_import_file:
            if key not in self.__possible_import_args or type(value) != type(self.__possible_import_args[key]):
                print(key, value, " are not a valid import arg value pair")
            else:
                self.__import_args[key] = value
        else:
            raise Exception("Cannot set import args")
    
    def set_export_arg(self, key, value):
        '''
        Sets/updates an export arguments value.
        '''
        if self.should_export_file:
            if key not in self.__possible_export_args or type(value) != type(self.__possible_export_args[key]):
                raise Exception(f"{key}, {value} are not a valid export arg value pair")
            else:
                self.__export_args[key] = value
                
        else:
            raise Exception("Cannot set export args")
        
    def add_args_from_dict(self, args_dict, import_or_export):
        '''
        Adds a subset of args to the parser from a dictionary. Provide a list of params to add. Key is the arg name, value is the arg value.
        '''
        if import_or_export == "import" and not self.should_import_file:
            raise NotImplementedError("Cannot add import args unless valid import file type specified")
        elif import_or_export == "export" and not self.should_export_file:
            raise NotImplementedError("Cannot add export args unless valid export file type is specified")
        elif import_or_export not in ["import", "export"]:
            raise Exception("Specify whether these are import or export args")
        
        if import_or_export == "import":
            assert all([arg in get_import_fn_args_dict(self.import_file_type) for arg in args_dict]), "Please make sure that the args list is valid for the import function you need to use. They must be a subset of {}".format(get_import_fn_args_dict(self.import_file_type))
            [self.set_import_arg(key, value) for key, value in args_dict.items()]
        else:
            assert all([arg in get_export_fn_args_dict(self.export_file_type) for arg in args_dict]), "Please make sure that the args list is valid for the export function you need to use. They must be a subset of {}".format(get_export_fn_args_dict(self.export_file_type))
            [self.set_export_arg(key, value) for key, value in args_dict.items()]
        
    def get_import_args_dict(self):
        return self.__import_args

    def get_export_args_dict(self):
        return self.__export_args
    
class ImportArgsManager(ImportExportArgManager):
    def __init__(self, import_file_type: str):
        super().__init__(import_file_type = import_file_type, should_import_file = True)
    
    def get_export_args_dict(self):
        raise NotImplementedError("Cannot get export args dict from this class")
        
    def set_export_arg(self):
        raise NotImplementedError("Cannot set export args dict from this class")

class ExportArgsManager(ImportExportArgManager):
    def __init__(self, export_file_type: str):
        super().__init__(export_file_type = export_file_type, should_export_file = True)
        
    def get_import_args_dict(self):
        raise NotImplementedError("Cannot get import args dict from this class")
        
    def set_import_arg(self):
        raise NotImplementedError("Cannot set import args dict from this class")




class ImportExportArgParser:
    
    def __init__(self, import_file_type: str = '', export_file_type: str = '', should_import_file: bool = False, should_export_file: bool = False):
        usage_text = ('''Use this tool to import/export files to blender. Supported formats: {}''').format(valid_formats)
        self.parser = argparse.ArgumentParser(description=usage_text)
        #composition more suitable here - the arg parser sets types and defaults and then reads in values - this is then stored in the ImportExportArgManager.
        #This could definitely  be refactored to avoid repetition.
        self.args_manager = ImportExportArgManager(import_file_type, export_file_type, should_import_file, should_export_file)
        
        
    def add_all_available_args_to_parser(self):
        self._add_specific_conversion_args()
        
    
    def add_args_from_dict(self, args_list, import_or_export):
        '''
        Adds a subset of args to the parser from a dictionary. Provide a list of params to add.
        '''
        #some of these checks are already performed by the args manager.
        if import_or_export == "import" and not self.args_manager.import_file:
            raise NotImplementedError("Cannot add import args unless import file type sepcified")
        elif import_or_export == "export" and not self.args_manager.export_file:
            raise NotImplementedError("Cannot add export args unless import file type sepcified")
        elif import_or_export not in ["import", "export"]:
            raise Exception("Specify whether these are import or export args")
        
        if import_or_export == "import":
            assert all([arg in get_import_fn_args_dict(self.args_manager.import_file_type) for arg in args_list]), "Please make sure that the args list is valid for the import function you need to use. They must be a subset of {}".format(get_import_fn_args_dict(self.import_file_type))
        else:
            assert all([arg in get_import_fn_args_dict(self.args_manager.import_file_type) for arg in args_list]), "Please make sure that the args list is valid for the export function you need to use. They must be a subset of {}".format(get_export_fn_args_dict(self.export_file_type))
        
        self._add_args_dict_to_parser(args_list, import_or_export)
    
    def _add_specific_conversion_args(self):
        '''
        Args to be passed in depend on the file type you are importing/exporting. This method automatically adds them based on file type.
        '''
        if self.args_manager.should_import_file:
            args_to_add = get_import_fn_args_dict(self.args_manager.import_file_type)
            self._add_args_dict_to_parser(args_to_add, "import")

        #already sanitised, no need to elif
        if self.args_manager.should_export_file:
            args_to_add = get_export_fn_args_dict(self.args_manager.export_file_type)
            self._add_args_dict_to_parser(args_to_add, "export")

            
    def _add_args_dict_to_parser(self, args_to_add: dict, import_or_export:str):
        '''
        Given an arg_name: default value dict, adds it to the command line arg parser. Overwrites value if already present.
        '''
        
        for key, val in args_to_add.items():
            self.parser.add_argument("-{}_".format(import_or_export)+key,
                            type=type(val),
                            dest = "{}_".format(import_or_export)+key,
                            required = key == "filepath",
                            default=val)
        
    def _parse_args(self):
        '''
        Parses command line args with call from blender.
        '''
        argv = get_cmd_line_args()
        return vars(self.parser.parse_known_args(argv)[0])
        
    def get_import_args_dict(self):
        '''
        An args dict that can be passed to the relevant import function
        '''
        import_args_dict = {key[7:]: value for key, value in self._parse_args().items() if key[:7] == "{}_".format("import")}
        self.args_manager.add_args_from_dict(import_args_dict, "import")
        return self.args_manager.get_import_args_dict()

    def get_export_args_dict(self):
        '''
        An args dict that can be passed to the relevant export function
        '''
        export_args_dict = {key[7:]: value for key, value in self._parse_args().items() if key[:7] == "{}_".format("export")}
        self.args_manager.add_args_from_dict(export_args_dict, "export")
        return self.args_manager.get_export_args_dict()
        
class ImportArgParser(ImportExportArgParser):
    def __init__(self, file_type):
        super().__init__(file_type, should_import_file = True)
    
    def get_export_args_dict(self):
        raise NotImplementedError("This is an importer, exporting not supported")



class ExportArgParser(ImportExportArgParser):
    def __init__(self, file_type):
        super().__init__(file_type, should_export_file = True)
        
    def get_import_args_dict(self):
        raise NotImplementedError("This is an exporter, importing not supported")
        
        
        
    
class ConverterArgParser(ImportExportArgParser):
    def __init__(self, import_file_type: str, export_file_type: str):
        super().__init__(import_file_type, export_file_type, should_import_file = True, should_export_file = True)
        
    
   
class fbx2objArgParser(ConverterArgParser):
    def __init__(self):
        super().__init__("fbx", "obj")