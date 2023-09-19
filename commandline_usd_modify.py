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
parser.add_argument("-TUSD", "--tfile", type=str, help="Target USD file", default="E:\\Blender_python\\hou_output.usd")

# set prim choice
parser.add_argument("-TP", "--tprim", nargs='+',  type=str, help="the target prim path")
parser.add_argument("-MP", "--mprim", nargs='+',  type=str, help="the material prim path")

# add trick to find if choice a mode
parser.add_argument("-M", "--modify", action='store_true', default=False, help="modify mode")
parser.add_argument("-A", "--append", action='store_true', default=False, help="append mode")
parser.add_argument("-SUB", "--subgeom", action='store_true', default=False, help="subgeom mode")
parser.add_argument("-D", "--delete", action='store_true', default=False, help="delete mode")

# set metadata
parser.add_argument("-UC", "--uclass", type=str, help="uclass, like StaticMesh")
parser.add_argument("-UP", "--uassetpath", type=str, help="uassetpath, like /Game/MyMesh")
parser.add_argument("-MB", "--matbind", type=str, help="material binding, set material path")
parser.add_argument("-GM", "--geommat", type=str, nargs='+', help="geom material path, can input a list")
args = parser.parse_args()

# check if the process mode choice
if args.modify + args.append + args.subgeom + args.delete != 1:
    exit("mode choice error")

# save common parser to meshinfo
usd_simple_filepath = "E:\\Blender_python\\BlenderPlugin\\bl-simple.usd"
target_prims = []
usdGenTookit.load_usd_files(args.tfile, usd_simple_filepath, meshInfo)
for primpath in args.tprim:
    target_prims.append(meshInfo.targetStage.GetPrimAtPath(primpath))

print(target_prims)
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
cachepath = "E:\\Blender_python\\BlenderPlugin\\bl-input.usd"
meshInfo.sourceStage.Export(cachepath)
bpy.ops.wm.usd_import(filepath="E:\\Blender_python\\BlenderPlugin\\bl-input.usd")
# do modify with the mesh


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
        usdGenTookit.append_prim(source_prims[i], target_prims[i], material_prim[i], meshInfo)  # set prim
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

meshInfo.targetStage.Export("E:\\Blender_python\\BlenderPlugin\\bl-output.usd")
print('process finished')
