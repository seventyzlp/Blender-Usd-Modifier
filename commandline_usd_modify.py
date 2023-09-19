from pxr import Usd, UsdGeom, Gf, Sdf, UsdShade
import usdGenTookit
import sys
import argparse
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
parser.add_argument("-SUSD", "--sfile", type=str, help="Source USD file", default="E:\\Blender_python\\blender_python_modify.usd")

# set prim choice
parser.add_argument("-TP", "--tprim", type=str, help="the target prim path")
parser.add_argument("-SP", "--sprim", type=str, help="the source prim path")
parser.add_argument("-MP", "--mprim", type=str, help="the material prim path")

# add trick to find if choice a mode
parser.add_argument("-M", "--modify",  action='store_true', default=False, help="modify mode")
parser.add_argument("-A", "--append",  action='store_true', default=False, help="append mode")
parser.add_argument("-SUB", "--subgeom", action='store_true', default=False, help="subgeom mode")
parser.add_argument("-D", "--delete",  action='store_true', default=False, help="delete mode")

# set metadata
parser.add_argument("-UC", "--uclass", type=str, help="uclass, like StaticMesh")
parser.add_argument("-UP", "--uassetpath", type=str, help="uassetpath, like /Game/MyMesh")
parser.add_argument("-MB", "--matbind", type=str, help="material binding, set material path")
parser.add_argument("-GM", "--geommat", type=str, nargs='+', help="geom material path, can input a list")
args = parser.parse_args()

# check if the process mode choice
# if args.modify + args.append + args.subgeom + args.delete != 1:
#     exit("mode choice error")

# save common parser to meshinfo
usdGenTookit.load_usd_files(args.tfile, args.sfile, meshInfo)
for type, path, name in meshInfo.sourceMeshPath:
    if args.sprim == path:
        source_prim = meshInfo.sourceStage.GetPrimAtPath(type)
for type, path, name in meshInfo.targetMeshPath:
    if args.tprim == path:
        target_prim = meshInfo.targetStage.GetPrimAtPath(type)

# start process
if args.modify:
    # modify mode
    usdGenTookit.replace_prim_mesh(source_prim, target_prim)
    print('modify')

elif args.append:
    # append mode
    meshInfo.uclass = args.uclass
    meshInfo.uassestpath = args.uassetpath
    material_prim = args.mprim

    usdGenTookit.append_prim(source_prim, target_prim, material_prim, meshInfo)  # set prim
    print('append')

elif args.delete:
    # delete mode
    usdGenTookit.delete_prim(target_prim, meshInfo)

elif args.subgeom:

    meshInfo.uclass = args.uclass
    meshInfo.uassestpath = args.uassetpath
    material_prim = args.mprim

    usdGenTookit.append_prim(source_prim, target_prim, material_prim, meshInfo)  # set prim
    
    for type, path, name in meshInfo.sourceMeshPath:
        if source_prim == path:
            source_prim = meshInfo.sourceStage.GetPrimAtPath(type)

    if source_prim.IsA(UsdGeom.Subset):
        meshInfo.sourceGeoms.append(source_prim)

    else:  # if not list all child prims
        for child_prim in source_prim.GetChildren():
            if child_prim.IsA(UsdGeom.Subset):
                meshInfo.sourceGeoms.append(child_prim)
    
    # get select sub and material
    for i in range(0, len(meshInfo.sourceGeoms)):
        geom_sub_material_selected = args.geommat[i]
        
                
        print(geom_sub_material_selected)
        geom_sub_mesh_selected = meshInfo.sourceGeoms[i]
        
        print(geom_sub_mesh_selected)
        usdGenTookit.modify_subgeom_material( geom_sub_material_selected ,geom_sub_mesh_selected, target_prim, source_prim, meshInfo)

meshInfo.targetStage.Export("E:\\Blender_python\\BlenderPlugin\\bl-output.usd")
print('process finished')
