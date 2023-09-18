from pxr import Usd, UsdGeom, Gf, Sdf, UsdShade
import bpy
import numpy as np
import math


def modify_prim_configure(prim, packagepath, uclass):
    prim.SetCustomDataByKey("PackagePath", packagepath)
    prim.SetCustomDataByKey("UClass", uclass)


def modify_subgeom_material(geom_sub_material_selected, geom_sub_mesh_selected, target_prim, source_prim, meshInfo):
    
    # add geomsubset to target usd
    parentprim_path = "".join(str(target_prim.GetPath())) + "/" + str(source_prim.GetPath()).split("/")[-1]
    parentprim = meshInfo.targetStage.GetPrimAtPath(parentprim_path)
    geomsubset_path = "".join(str(parentprim.GetPath())) + "/" + str(geom_sub_mesh_selected.GetPath()).split("/")[-1]
    geomsubset = meshInfo.targetStage.DefinePrim(geomsubset_path, "GeomSubset")

    # set material to subset
    material = UsdShade.Material.Get(meshInfo.targetStage, Sdf.Path(geom_sub_material_selected))
    mbindapi = UsdShade.MaterialBindingAPI(geomsubset)
    mbindapi.Bind(material=material)

    # set metadata
    geomsubset.CreateAttribute("elementType", Sdf.ValueTypeNames.Token).Set(geom_sub_mesh_selected.GetAttribute('elementType').Get())
    geomsubset.CreateAttribute("indices", Sdf.ValueTypeNames.UInt64Array).Set(geom_sub_mesh_selected.GetAttribute('indices').Get())
    geomsubset.CreateAttribute("familyName", Sdf.ValueTypeNames.Token).Set(geom_sub_mesh_selected.GetAttribute('familyName').Get())
    

def replace_prim_mesh(source_prim, target_prim):

    points = UsdGeom.Mesh(source_prim).GetPointsAttr().Get()
    faceVertexCounts = UsdGeom.Mesh(source_prim).GetFaceVertexCountsAttr().Get()
    faceVertexIndices = UsdGeom.Mesh(source_prim).GetFaceVertexIndicesAttr().Get()

    # match points
    UsdGeom.Mesh(target_prim).CreatePointsAttr().Set(points)
    UsdGeom.Mesh(target_prim).CreateFaceVertexCountsAttr().Set(faceVertexCounts)
    UsdGeom.Mesh(target_prim).CreateFaceVertexIndicesAttr().Set(faceVertexIndices)
    trans = get_world_transform_xform(source_prim)

    # match normal
    normals = source_prim.GetAttribute('normals').Get()
    for i in range(len(normals)):
        normals[i] = tuple(map(lambda x: -x, normals[i]))
    target_prim.CreateAttribute('normals', Sdf.ValueTypeNames.Normal3fArray).Set(normals)

    # match uv
    uv = source_prim.GetAttribute('primvars:st').Get()
    if uv:
        target_prim.CreateAttribute('primvars:st', Sdf.ValueTypeNames.TexCoord2fArray).Set(uv)
        UsdGeom.Primvar(target_prim.GetAttribute('primvars:st')).SetInterpolation('faceVarying')

    # match transform
    trans[0][2], trans[0][1] = trans[0][1], trans[0][2]
    trans[1][2], trans[1][1] = trans[1][1], trans[1][2]
    trans[2][2], trans[2][1] = trans[2][1], trans[2][2]

    xformapi = UsdGeom.XformCommonAPI(target_prim)
    xformapi.SetRotate(Gf.Vec3f(trans[1][0] - 90, trans[1][1], trans[1][2]))
    print
    xformapi.SetScale(Gf.Vec3f(trans[2][0], trans[2][1], trans[2][2]) * 0.01)
    xformapi.SetTranslate(Gf.Vec3d(trans[0][0], trans[0][1], trans[0][2]) * 0.01)

    # set uv
    UsdGeom.Primvar(target_prim.GetAttribute('normals')).SetInterpolation('faceVarying')


def append_prim(source_prim, parent_prim, meshInfo):

    # create empty child prim
    childprimpath = "".join(str(parent_prim.GetPath())) + "/" + str(source_prim.GetPath()).split("/")[-1]
    childprim = meshInfo.targetStage.DefinePrim(childprimpath, "Mesh")

    # copy mesh attributes to child prim
    replace_prim_mesh(source_prim, childprim)

    # add custom data
    meshInfo.uclass = bpy.context.scene.uclass
    meshInfo.uassestpath = bpy.context.scene.uassetpath
    if meshInfo.uassestpath and meshInfo.uclass:
        modify_prim_configure(childprim, meshInfo.uassestpath, meshInfo.uclass)

    # set material bindings
    target_prim_selected = bpy.context.scene.prim_material
    for type, path, name in meshInfo.targetMeshPath:
        if target_prim_selected == path:
            meshInfo.materialpath = target_prim_selected

    if meshInfo.materialpath:
        material = UsdShade.Material.Get(meshInfo.targetStage, Sdf.Path(meshInfo.materialpath))
        mbindapi = UsdShade.MaterialBindingAPI(childprim)
        mbindapi.Bind(material=material)

    # set leftorientation
    childprim.CreateAttribute('orientation', Sdf.ValueTypeNames.Token).Set('leftHanded')

    # set subdivision
    childprim.CreateAttribute('subdivisionScheme', Sdf.ValueTypeNames.Token).Set('none')


def delete_prim(prim, meshInfo):
    meshInfo.targetStage.RemovePrim(prim.GetPath())


def get_world_transform_xform(prim: Usd.Prim):

    xform = UsdGeom.Xformable(prim)
    time = Usd.TimeCode.Default()  # The time at which we compute the bounding box
    world_transform: Gf.Matrix4d = xform.ComputeLocalToWorldTransform(time)
    matrix = np.array(world_transform)

    rot_matrix = matrix[:3, :3]
    rot_matrix_inv = np.linalg.inv(rot_matrix)

    angles = np.degrees(
        np.around(np.array([
            math.atan2(rot_matrix_inv[2, 1], rot_matrix_inv[2, 2]),
            math.atan2(-rot_matrix_inv[2, 0], math.sqrt(rot_matrix_inv[2, 1]**2 + rot_matrix_inv[2, 2]**2)),
            math.atan2(rot_matrix_inv[1, 0], rot_matrix_inv[0, 0])
        ]),
                  decimals=6))

    translation: Gf.Vec3d = world_transform.ExtractTranslation()
    scale: Gf.Vec3d = Gf.Vec3d(*(v.GetLength() for v in world_transform.ExtractRotationMatrix()))

    return translation, angles, scale,


def collect_prims(prim, prim_dict):
    prim_dict[prim.GetPath()] = prim

    for child in prim.GetChildren():
        collect_prims(child, prim_dict)
