import bpy
import os
# from argparse import ArgumentParser
#
# argdef = ArgumentParser(description='Process a Blender file from the command line.')
# argdef.add_argument('infile', type=str, help='Input file')
# argdef.add_argument('outfile', type=str, help='Output file')
# argdef.add_argument('--target', '-t', type=str, help='Target object to modify')
#
# args = argdef.parse_args()

infile = os.environ['INPUT_FILE']
outfile = os.environ['OUTPUT_FILE']
targetname = os.environ['TARGET']

# clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.outliner.orphans_purge()
print('Cleared scene')

# load scene
if infile.startswith('omniverse://'):
    bpy.context.scene.omni_nucleus.filepath = infile
    bpy.ops.omni.import_usd()
else:
    bpy.ops.wm.usd_import(filepath=infile)
print(f'Loaded {infile}')

# do the real deal here
if targetname:
    targetname = targetname.split('/')[-1]
    target = bpy.data.objects[targetname]
    target.modifiers.new('Remesh', 'REMESH')
    deform = target.modifiers.new('Simple Deform', 'SIMPLE_DEFORM')
    deform.deform_method = 'TWIST'
    deform.angle = 3.14159
    deform.deform_axis = 'X'
    target.modifiers.new('Triangulate', 'TRIANGULATE')
    print(f'Added modifiers to {targetname}')


# export scene
if outfile.startswith('omniverse://'):
    bpy.context.scene.omni_nucleus.filepath = outfile
    bpy.ops.omni.export_usd()
else:
    bpy.ops.wm.usd_export(filepath=outfile)
print(f'Exported to {outfile}')
