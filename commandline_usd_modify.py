from pxr import Usd, UsdGeom, Gf, Sdf, UsdShade
import usdGenTookit
import sys
import argparse
import bpy
'''
use script argparse after -- to seperate with blender
'''


class ArgumentParserForBlender(argparse.ArgumentParser):

    def _get_argv_after_doubledash(self):
        try:
            idx = sys.argv.index("--")
            return sys.argv[idx + 1:]  # the list after '--'
        except ValueError as e:  # '--' not in the list:
            return []

    # overrides superclass
    def parse_args(self):
        return super().parse_args(args=self._get_argv_after_doubledash())


meshInfo = usdGenTookit.PrimMeshINFO()
parser = ArgumentParserForBlender()
# set usd file
parser.add_argument("-TUSD", "--tfile", type=str, help="Target USD file", default="hou_output.usd")

# set prim choice
parser.add_argument("-TP", "--tprim", nargs='+',  type=str, help="the target prim path")
parser.add_argument("-MP", "--mprim", nargs='+',  type=str, help="the material prim path")
parser.add_argument("-PP", "--pprim", nargs='+',  type=str, help="the parent prim path for append")

# add trick to find if choice a mode
parser.add_argument("-M", "--modify", action='store_true', default=False, help="modify mode")
parser.add_argument("-A", "--append", action='store_true', default=False, help="append mode")
parser.add_argument("-SUB", "--subgeom", action='store_true', default=False, help="subgeom mode")
parser.add_argument("-D", "--delete", action='store_true', default=False, help="delete mode")

# set metadata
parser.add_argument("-UC", "--uclass", type=str, help="uclass, like StaticMesh")
parser.add_argument("-UP", "--uassetpath", type=str, help="uassetpath, like /Game/MyMesh")
parser.add_argument("-GM", "--geommat", type=str, nargs='+', help="geom material path, can input a list")
args = parser.parse_args()

# check if the process mode choice
if args.modify + args.append + args.subgeom + args.delete != 1:
    exit("mode choice error")

# save common parser to meshinfo
usd_simple_filepath = "BlenderPlugin\\bl-simple.usd"
target_prims = []
usdGenTookit.load_usd_files(args.tfile, usd_simple_filepath, meshInfo)
for primpath in args.tprim:
    target_prims.append(meshInfo.targetStage.GetPrimAtPath(primpath))
    
# generate cache
for type, path, name in meshInfo.sourceMeshPath:
    if path == '/root':
        parent_prim = meshInfo.sourceStage.GetPrimAtPath(type)

# add target mesh to cache usd
source_prims = []
for target_prim in target_prims:
    childprimpath = "".join(str(parent_prim.GetPath())) + "/" + str(target_prim.GetPath()).split("/")[-1]
    childprim = meshInfo.sourceStage.DefinePrim(childprimpath, "Mesh")
    usdGenTookit.replace_temp_prim_mesh(target_prim, childprim)
    source_prims.append(childprim)

# export cache usd
cachepath = "BlenderPlugin\\bl-input.usd"
meshInfo.sourceStage.Export(cachepath)
bpy.ops.wm.usd_import(filepath=cachepath)

# do modify with the mesh
import use_geometrynode

obj = bpy.context.scene.objects.get('grid')
modify = obj.modifiers.new(name="MY MDF", type='NODES')
modify.node_group = use_geometrynode.geometry_nodes
bpy.context.view_layer.objects.active = obj  # need to choice the target mesh
print(bpy.ops.object.modifier_apply(modifier='MY MDF'))
blender_modifiedpath = "blender_python_modify.usd"
bpy.ops.wm.usd_export(filepath=blender_modifiedpath)

source_prims = []
target_prims = []

usdGenTookit.load_usd_files(args.tfile, blender_modifiedpath, meshInfo)
for primpath in args.tprim:
    target_prims.append(meshInfo.targetStage.GetPrimAtPath(primpath))
    
for target_prim in target_prims:
    source_prims.append(meshInfo.sourceStage.GetPrimAtPath('/root/' + str(target_prim.GetPath()).split("/")[-1]+"/"+ str(target_prim.GetPath()).split("/")[-1]))
    
print('============source======================')
print(source_prims)
print('============target======================')
print(target_prims)

# start process
if args.modify:
    # modify mode
    for i in range(0, len(source_prims)):
        usdGenTookit.replace_prim_mesh(source_prims[i], target_prims[i])
        print('modify')

elif args.append:
    # append mode
    meshInfo.uclass = args.uclass
    meshInfo.uassestpath = args.uassetpath
    material_prim = args.mprim
    for i in range(0, len(source_prims)):
        usdGenTookit.append_prim(source_prims[i], meshInfo.targetStage.GetPrimAtPath(args.pprim[i]), material_prim[i], meshInfo)  # set prim
        print('append')

elif args.delete:
    # delete mode
    for target_prim in target_prims:
        usdGenTookit.delete_prim(target_prim, meshInfo)

elif args.subgeom:

    meshInfo.uclass = args.uclass
    meshInfo.uassestpath = args.uassetpath
    material_prim = args.mprim

    for i in range(0, len(source_prims)):

        usdGenTookit.append_prim(source_prims[i], target_prims[i], material_prim[i], meshInfo)  # set prim

        for type, path, name in meshInfo.sourceMeshPath:
            if source_prims[i] == path:
                source_prims[i] = meshInfo.sourceStage.GetPrimAtPath(type)

        if source_prims[i].IsA(UsdGeom.Subset):
            meshInfo.sourceGeoms.append(source_prims[i])

        else:  # if not list all child prims
            for child_prim in source_prims[i].GetChildren():
                if child_prim.IsA(UsdGeom.Subset):
                    meshInfo.sourceGeoms.append(child_prim)

        # get select sub and material
        for j in range(0, len(meshInfo.sourceGeoms)):
            geom_sub_material_selected = args.geommat[j]

            print(geom_sub_material_selected)
            geom_sub_mesh_selected = meshInfo.sourceGeoms[j]

            print(geom_sub_mesh_selected)
            usdGenTookit.modify_subgeom_material(geom_sub_material_selected, geom_sub_mesh_selected, target_prims[i], source_prims[i], meshInfo)

        print('geom')

meshInfo.targetStage.Export("BlenderPlugin\\bl-output.usd")
print('process finished')
