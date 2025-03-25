import bpy
from dataclasses import dataclass
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf
import usdGenTookit
import bpy_extras

bl_info = {
    "name": "USD Modify",
    "blender": (2, 80, 0),
    "category": "Object",
    "author": "millozhang"
}

meshInfo = usdGenTookit.PrimMeshINFO()

def update_target_enum_items(self, context):
    items = []
    for item in meshInfo.targetMeshPath:
        items.append(item)
    return items


def update_source_enum_items(self, context):
    items = []
    for item in meshInfo.sourceMeshPath:
        items.append(item)
    return items


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.target_enum = bpy.props.EnumProperty(
        name="target path",
        items=update_target_enum_items,
    )
    bpy.types.Scene.source_enum = bpy.props.EnumProperty(
        name="source path",
        items=update_source_enum_items,
    )
    bpy.types.Scene.prim_material = bpy.props.EnumProperty(name="prim material", items=update_target_enum_items)

    bpy.types.Scene.target_path = bpy.props.StringProperty(
        name="target file path",
        default="",
        description="target file path",
    )
    bpy.types.Scene.filesavepath = bpy.props.StringProperty(
        name="file save path",
        default='',
        description="file save path",
    )
    bpy.types.Scene.uclass = bpy.props.StringProperty(
        name="uclass",
        default="",
        description="uclass",
    )
    bpy.types.Scene.uassetpath = bpy.props.StringProperty(
        name="uassetpath",
        default="",
        description="uassetpath",
    )


def unregister():
    for cls in _classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.target_enum
    del bpy.types.Scene.source_enum
    del bpy.types.Scene.target_path
    del bpy.types.Scene.filesavepath
    del bpy.types.Scene.uclass
    del bpy.types.Scene.uassetpath
    del bpy.types.Scene.geom_enum
    del bpy.types.Scene.prim_material

    for i in range(0, len(meshInfo.sourceGeoms)):
        delattr(bpy.types.Scene, f'geom_enum_{i}')


class GetSourceButton(bpy.types.Operator):
    bl_idname = "get_source_button.button"
    bl_label = "Simplify Source Object"

    def get_object_path(self):
        obj = bpy.context.view_layer.objects.active
        if obj is not None:
            return obj.name

    def execute(self, context):

        name = self.get_object_path()
        for mesh in meshInfo.sourceMeshPath:
            if not name in mesh[1]:
                meshInfo.sourceMeshPath.remove(mesh)

        return {'FINISHED'}


class GetSourceMeshButton(bpy.types.Operator):
    bl_idname = "get_source_mesh_button.button"
    bl_label = "Show Source Mesh"

    def execute(self, context):

        if len(meshInfo.sourceMeshPath) == 5:  # if stage has no mesh prim
            # get choice target mesh
            target_prim_selected = bpy.context.scene.target_enum
            for type, path, name in meshInfo.targetMeshPath:
                if target_prim_selected == path:
                    target_prim = meshInfo.targetStage.GetPrimAtPath(type)

            for type, path, name in meshInfo.sourceMeshPath:
                if path == '/root':
                    parent_prim = meshInfo.sourceStage.GetPrimAtPath(type)

            # add target mesh to cache usd
            childprimpath = "".join(str(parent_prim.GetPath())) + "/" + str(target_prim.GetPath()).split("/")[-1]
            childprim = meshInfo.sourceStage.DefinePrim(childprimpath, "Mesh")
            usdGenTookit.replace_temp_prim_mesh(target_prim, childprim)

            # add the usd to stage
            meshInfo.sourceStage.Export(meshInfo.savePath + "BlenderPlugin\\bl-input.usd")
            bpy.ops.wm.usd_import(filepath=meshInfo.savePath + "BlenderPlugin\\bl-input.usd")

        return {'FINISHED'}


class GetUsdButton(bpy.types.Operator):
    bl_idname = "get_usd_button.button"
    bl_label = "Get USD Objects"

    def execute(self, context):
        # reset to default
        meshInfo.reset_source()
        meshInfo.reset_target()
        bpy.context.scene.uclass = meshInfo.uclass
        bpy.context.scene.uassetpath = meshInfo.uassestpath

        # save current scene to usd
        bpy.ops.wm.usd_export(filepath=meshInfo.savePath + "\\blender_python_modify.usd")

        meshInfo.targetPath = bpy.context.scene.target_path  # usd cached choice

        print(meshInfo.targetPath)

        input_target_file = meshInfo.targetPath
        input_source_file = meshInfo.savePath + "\\blender_python_modify.usd"

        usdGenTookit.load_usd_files(input_target_file, input_source_file, meshInfo)
        return {'FINISHED'}


class GetGeomSubset(bpy.types.Operator):
    bl_idname = "get_geom_subset.button"
    bl_label = "Get Geom Subset"

    meshInfo.sourceGeoms.clear()

    def execute(self, context):
        # get all GeomsSubset
        source_prim_selected = bpy.context.scene.source_enum
        if source_prim_selected:
            for type, path, name in meshInfo.sourceMeshPath:
                if source_prim_selected == path:
                    source_prim = meshInfo.sourceStage.GetPrimAtPath(type)

            if source_prim.IsA(UsdGeom.Subset):
                meshInfo.sourceGeoms.append(source_prim)

            else:  # if not list all child prims
                for child_prim in source_prim.GetChildren():
                    if child_prim.IsA(UsdGeom.Subset):
                        meshInfo.sourceGeoms.append(child_prim)

        # register geommesh selection enum
        for j in range(0, len(meshInfo.sourceGeoms)):
            print(f"create enum {j}")
            setattr(bpy.types.Scene, f'geom_enum_{j}', bpy.props.EnumProperty(
                name=f"geom {j}",
                items=update_target_enum_items,
            ))

        return {'FINISHED'}


class DoModifyButton(bpy.types.Operator):
    bl_idname = "do_modify_button.button"
    bl_label = "Do Modify"

    def execute(self, context):

        source_prim_selected = bpy.context.scene.source_enum
        target_prim_selected = bpy.context.scene.target_enum

        if source_prim_selected and target_prim_selected:

            # copy prim source mesh to target mesh
            for type, path, name in meshInfo.targetMeshPath:
                if target_prim_selected == path:
                    target_prim = meshInfo.targetStage.GetPrimAtPath(type)

            for type, path, name in meshInfo.sourceMeshPath:
                if source_prim_selected == path:
                    source_prim = meshInfo.sourceStage.GetPrimAtPath(type)

            usdGenTookit.replace_prim_mesh(source_prim, target_prim)
            meshInfo.targetStage.Export(meshInfo.savePath + "\\BlenderPlugin\\bl-output.usd")
            print(meshInfo.savePath + "\\BlenderPlugin\\bl-output.usd")
            print("modify")
        else:
            print("Please choose source and target prim")

        return {'FINISHED'}


class DoAppendButton(bpy.types.Operator):
    bl_idname = "do_append_button.button"
    bl_label = "Do Append"

    def execute(self, context):

        # if add prim, the target prim will be parent prim
        source_prim_selected = bpy.context.scene.source_enum
        target_prim_selected = bpy.context.scene.target_enum

        if source_prim_selected and target_prim_selected:

            # copy prim source mesh to target mesh
            for type, path, name in meshInfo.sourceMeshPath:
                if source_prim_selected == path:
                    source_prim = meshInfo.sourceStage.GetPrimAtPath(type)
            for type, path, name in meshInfo.targetMeshPath:
                if target_prim_selected == path:
                    target_prim = meshInfo.targetStage.GetPrimAtPath(type)

            meshInfo.uclass = bpy.context.scene.uclass
            meshInfo.uassestpath = bpy.context.scene.uassetpath
            material_prim = bpy.context.scene.prim_material

            usdGenTookit.append_prim(source_prim, target_prim, material_prim, meshInfo)  # set prim
            meshInfo.targetStage.Export(meshInfo.savePath + "\\BlenderPlugin\\bl-output.usd")

            print("append")
        else:
            print("Please choose source and target prim")

        return {'FINISHED'}


class DoDeleteButton(bpy.types.Operator):
    bl_idname = "do_delete_button.button"
    bl_label = "Do Delete"

    # delete target prim
    def execute(self, context):
        target_prim_selected = bpy.context.scene.target_enum
        for type, path, name in meshInfo.targetMeshPath:
            if target_prim_selected == path:
                target_prim = meshInfo.targetStage.GetPrimAtPath(type)

        usdGenTookit.delete_prim(target_prim, meshInfo)
        meshInfo.targetStage.Export(meshInfo.savePath + "\\BlenderPlugin\\bl-output.usd")
        print('remove prim')

        return {'FINISHED'}


class DoModifyGeomSubSetButton(bpy.types.Operator):
    bl_idname = "do_modify_geom_subset_button.button"
    bl_label = "Do Modify GeomSubset Material"

    def execute(self, context):
        source_prim_selected = bpy.context.scene.source_enum
        target_prim_selected = bpy.context.scene.target_enum
        material_prim = bpy.context.scene.prim_material

        # add mesh parent to target usd
        for type, path, name in meshInfo.sourceMeshPath:
            if source_prim_selected == path:
                source_prim = meshInfo.sourceStage.GetPrimAtPath(type)
        for type, path, name in meshInfo.targetMeshPath:
            if target_prim_selected == path:
                target_prim = meshInfo.targetStage.GetPrimAtPath(type)

        usdGenTookit.append_prim(source_prim, target_prim, material_prim, meshInfo)  # set prim

        # get select sub and material
        for i in range(0, len(meshInfo.sourceGeoms)):
            geom_sub_material_selected = getattr(bpy.context.scene, f'geom_enum_{i}')
            geom_sub_mesh_selected = meshInfo.sourceGeoms[i]
            usdGenTookit.modify_subgeom_material(geom_sub_material_selected, geom_sub_mesh_selected, target_prim, source_prim, meshInfo)

        meshInfo.targetStage.Export(meshInfo.savePath + "\\BlenderPlugin\\bl-output.usd")
        return {'FINISHED'}


class ChoiceTargetButton(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "choice_target_button.button"
    bl_label = "Choice Target"

    files = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def execute(self, context):  # set target file
        meshInfo.targetPath = self.filepath
        bpy.context.scene.target_path = self.filepath
        return {'FINISHED'}


class ChoiceSavePathButton(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "choice_save_path_button.button"
    bl_label = "Choice Save Path"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.filesavepath = self.filepath
        meshInfo.savePath = self.filepath.replace("\\", "\\\\")
        return{'FINISHED'}


class USDModifyPanel(bpy.types.Panel):
    bl_label = "USD Modify"
    bl_idname = "_PT_USD_modify_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "USD Modify"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator(ChoiceTargetButton.bl_idname, icon="FILE_FOLDER")
        row.prop(context.scene, "target_path", text="")

        row = layout.row()
        row.operator(ChoiceSavePathButton.bl_idname, icon="FILE_FOLDER")
        row.prop(context.scene, "filesavepath", text="")

        row = layout.row()
        spilt = row.split(factor=0.5)
        spilt.label(text="Choose source mesh")
        spilt.prop(context.scene, "source_enum", text="")

        row = layout.row()
        spilt = row.split(factor=0.5)
        spilt.label(text="")  # just for space
        spilt.operator(GetSourceMeshButton.bl_idname, icon="OUTLINER_OB_MESH")

        row = layout.row()
        spilt = row.split(factor=0.5)
        spilt.label(text="Choose target mesh")
        spilt.prop(context.scene, "target_enum", text="")

        row = layout.row()
        spilt = row.split(factor=0.5)
        spilt.operator(GetUsdButton.bl_idname, icon="TEXT")
        spilt.operator(GetSourceButton.bl_idname)

        row = layout.row()
        spilt = row.split(factor=0.5)
        spilt.operator(DoModifyButton.bl_idname)
        spilt.operator(DoDeleteButton.bl_idname, icon="GHOST_DISABLED")


class USDAppendPannel(bpy.types.Panel):
    bl_label = "USD Append"
    bl_idname = "_PT_USD_append_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "_PT_USD_modify_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        spilt = row.split(factor=0.5)
        spilt.label(text="UClass")
        spilt.prop(context.scene, "uclass", text="")

        row = layout.row()
        spilt = row.split(factor=0.5)
        spilt.label(text="UEAsset Path")
        spilt.prop(context.scene, "uassetpath", text="")

        row = layout.row()
        spilt = row.split(factor=0.5)
        spilt.label(text="material binding")
        spilt.prop(context.scene, "prim_material", text="")

        row = layout.row()
        row.operator(DoAppendButton.bl_idname)


class USDModifyGeomSubset(bpy.types.Panel):
    bl_label = "USD Modify Geomsubset"
    bl_idname = "_PT_USD_modify_geom_subset"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "_PT_USD_modify_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator(GetGeomSubset.bl_idname)

        if meshInfo.sourceGeoms:

            i = 0
            for geom in meshInfo.sourceGeoms:
                row = layout.row()
                spilt = row.split(factor=0.5)
                spilt.label(text=str(geom.GetPath()))
                spilt.prop(context.scene, f"geom_enum_{i}", text="")
                i += 1

            if i == len(meshInfo.sourceGeoms) and i != 0:  # if find geomsubset
                row = layout.row()
                row.operator(DoModifyGeomSubSetButton.bl_idname)


_classes = [
    GetSourceButton, USDModifyPanel, GetUsdButton, DoModifyButton, ChoiceTargetButton, DoAppendButton, USDAppendPannel, USDModifyGeomSubset,
    GetGeomSubset, DoModifyGeomSubSetButton, DoDeleteButton, GetSourceMeshButton,ChoiceSavePathButton
]

if __name__ == "__main__":
    register()
