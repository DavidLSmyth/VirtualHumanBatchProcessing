from bpy.props import *
from .combiner_ops import *
from .packer import BinPacker
from ... import globs


class Combiner(bpy.types.Operator):
    bl_idname = 'smc.combiner'
    bl_label = 'Create Atlas'
    bl_description = 'Combine materials'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    directory = StringProperty(maxlen=1024, default=r'D:\SAUCEFiles\MixamoCharacters\MixamoChars\unpackedTextures', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob = StringProperty(default='', options={'HIDDEN'})
    cats = BoolProperty(default=False)
    data = None
    mats_uv = None
    structure = None

    def execute(self, context):
        scn = context.scene
        scn.smc_save_path = self.directory
        scn.smc_save_path = r'D:\SAUCEFiles\MixamoCharacters\MixamoChars\unpackedTextures'
        print("Using save path: ", scn.smc_save_path)
        #print("self.structure: ",self.structure)
        self.structure = BinPacker(get_size(scn, self.structure)).fit()
        size = (max([i['gfx']['fit']['x'] + i['gfx']['size'][0] for i in self.structure.values()]),
                max([i['gfx']['fit']['y'] + i['gfx']['size'][1] for i in self.structure.values()]))
        if any(size) > 20000:
            self.report({'ERROR'}, 'Output image size is too large')
            return {'FINISHED'}
        atlas = get_atlas(scn, self.structure, size)
        get_aligned_uv(scn, self.structure, atlas.size)
        assign_comb_mats(scn, self.data, self.mats_uv, atlas)
        clear_mats(self.mats_uv)
        bpy.ops.smc.refresh_ob_data()
        self.report({'INFO'}, 'Materials were combined.')
        return {'FINISHED'}

    def invoke(self, context, event):
        print("invoked")
        
        scn = context.scene
        bpy.ops.smc.refresh_ob_data()
        if self.cats:
            scn.smc_size = 'PO2'
            scn.smc_gaps = 16.0
        set_ob_mode(context.view_layer if globs.version > 0 else scn)
        self.data = get_data(scn.smc_ob_data)
        self.mats_uv = get_mats_uv(self.data)
        clear_empty_mats(self.data, self.mats_uv)
        get_duplicates(self.mats_uv)
        self.structure = get_structure(self.data, self.mats_uv)
        if globs.version == 0:
            context.space_data.viewport_shade = 'MATERIAL'
        if (len(self.structure) == 1) and next(iter(self.structure.values()))['dup']:
            try:
                clear_duplicates(self.structure)
            except Exception as e:
                print("could not clear duplicates")
            bpy.ops.smc.refresh_ob_data()
            self.report({'INFO'}, 'Duplicates were combined')
            return {'FINISHED'}
        elif not self.structure or (len(self.structure) == 1):
            bpy.ops.smc.refresh_ob_data()
            self.report({'ERROR'}, 'No unique materials selected')
            return {'FINISHED'}
        #context.window_manager.fileselect_add(self)
        return self.execute(context)
        #return {'RUNNING_MODAL'}
