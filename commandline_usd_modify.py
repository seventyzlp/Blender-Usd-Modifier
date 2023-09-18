from pxr import Usd, UsdGeom, Gf, Sdf
import usdGenTookit
# import argparse

# parser = argparse.ArgumentParser(description='file path message')
# parser.add_argument('--TUSD','-t', type=str, default="E:\\Blender_python\\hou_output.usd", help='target usd file')
# parser.add_argument('--SUSD','-s', type=str, default="E:\\Blender_python\\blender_output.usd", help='source usd file')
# args = parser.parse_args()

# input_usd_file = args.TUSD
# input_modified_usd_file = args.SUSD


input_usd_file = "E:\\Blender_python\\hou_output.usd"
input_modified_usd_file = "E:\\Blender_python\\blender_output.usd"

target_stage = Usd.Stage.Open(input_usd_file)
source_stage = Usd.Stage.Open(input_modified_usd_file)

target_prim_dict = {}
source_prim_dict = {}
usdGenTookit.collect_prims(target_stage.GetPseudoRoot(), target_prim_dict)
usdGenTookit.collect_prims(source_stage.GetPseudoRoot(), source_prim_dict)

# the source stage is unknown, so need to get
for prim_path, prim in source_prim_dict.items():
    print(f"{prim_path}: {prim}")
source_prim_input = input("Input Source Prim Path: ")

for prim_path, prim in target_prim_dict.items():
    print(f"{prim_path}: {prim}")
target_prim_input = input("Input Target Prim Path: ")

source_prim = source_prim_dict[Sdf.Path(source_prim_input)]
target_prim = target_prim_dict[Sdf.Path(target_prim_input)]

print(source_prim)

usdGenTookit.replace_prim_mesh(source_prim, target_prim)

output_usd_file = "E:\\Blender_python\\hou_output_with_modify.usd"
target_stage.Export(output_usd_file)

print("Done")
