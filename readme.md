# blender 接入usd 工作流

## blender 插件: usd_modify.py
[usd-modify.py](/usd_modify.py)

![工具界面](/pic/blender插件界面.png)

### 使用方法
1. 点Choice Target按钮选择想要修改的符合flow格式的usd文件
2. 点Choice Save Path 来选择输出文件和cache文件的保存位置
3. (可选)在blender中创建一个新的mesh，来替换目标usd中的某个prim
4. 点Get Usd Objects获取当前编辑窗口和目标usd的信息
5. 在choose source mesh 和 choose target mesh 中选择修改后的新prim和usd中的旧prim
6. (可选)点击Show Source Mesh，会把usd中的物体输入到blender窗体中，把目标usd中的东西拿到blender来编辑
   - 这么做之后，需要重新点Get Usd Object 刷新临时usd文件, 然后可以在Choose usd sourse菜单中看到刚刚编辑的东西
7. 把修改后的东西导入到符合flow格式的usd文件中
   -  点Do Modify: 把target prim 用 source prim 进行替换
   -  点Do delete: 把target prim 从 usd 里面删掉
   -  点Do Append: 以target prim 为父 添加子prim为 source prim，可以选择设置prim的元数据 uclass 和 uasset path
   -  点Do Modify GeomSubset Material: 如果source mesh 有 geomsubset, 那么需要点击get geom subset, 选中材质的绑定之后，可以同步geomsubset
8. 获取输出的符合flow 格式的usd: bl-output.usd

另外，如果在活动视图中选中了想要的source mesh，那么在点击Simplify Source Object可以对Choose source mesh下拉框中的
选项进行筛选，把非选中对象相关的prim不显示(但是依然存在)

**另外，一定要应用修改器才能让几何节点的效果实现，否则blender在导出usd时，会忽略未应用的修改器效果。**

### 使用流程中的usd缓存文件

1. 需要修改的目标usd文件: hou-output.usd，可以是任何别的usd
2. 把当前blender活动视图中的所有内容转换成的usd文件: blender-python-modify.usd
3. 输出的usd文件: bl-output.usd

### 使用GeomSubset时的测试文件

[sub.blend](/BlenderPlugin/sub.blend)

![工程打开图](/pic/sub.png)

对这个物体使用插件进行替换的情况为图1所示，可以看到在最下面能够选择GeomSubSet的材质设置

## 命令行工具: commandline_usd_modify.py
![流程实现](/pic/blender插件工作流程'commandline'.png)

[commandline_usd_modify.py](/commandline_usd_modify.py)

### 使用方法

需要使用omniverse版本的blender.exe 在控制台执行这个python文件，需要输入的是目标prim路径和操作模式。

为了防止blender的启动参数与脚本的输入参数混淆，**需要在设置完毕blender的启动参数之后，输入 -- 后，再输入命令行的参数**

参考执行命令：.\blender.exe -b --python E:\Blender_python\commandline_usd_modify.py -- -TP /Octpus/spikes/grid -MP /_UAssets/M_Box -FP /Octpus/spikes -A

1. --tfile: 设置符合flow格式的usd文件路径
2. --sfilepath: 设置usd文件保存路径，如果没有的话默认使用commandline_usd_modify.py 的位置
3. --tprim: 设置目标prim在 usd中的路径，可以并列添加多个
4. --mprim: 当Append prim时，绑定于prim上的材质prim的路径
5. --pprim: 当Append prim时，新添加prim的父prim路径
6. --modify: 替换prim
7. --append: 添加新prim到父prim下
8. --delete: 把prim删掉
9. --subgeom: 替换geomsubset的内容
10. --uclass: 当添加时，设置prim metadata中 uclass的值
11. --uassetpath: 当添加时，设置prim metadata中 uassetpath的值
12. --geommat: 设置geomsubset的材质

### 使用流程中的usd缓存文件

1. 需要修改的目标usd文件: hou-output.usd，可以是任何别的usd
2. 已知格式的usd文件：bl-simple.usd, 目前使用的是由blender空场景生成的usd
3. (debug)把想要修改的prim添加到bl-simple.usd后，没有进行其他处理的usd: bl-input.usd
4. (debug)对添加的prim进行修改后的的bl-input.usd: blender-python-modify.usd
5. 输出的usd文件: bl-output.usd

### hou-output.usd的prim结构

测试用
- / 
- /Octpus 
- /Octpus/spikes -- (mesh)
- /Octpus/spikes/box -- 点的数据被我删掉了，所以在hou-output.usd中看不见(mesh)
- /Octpus/spikes/grid -- (mesh)
- /_UAssets 
- /_UAssets/M_Box -- (material)
- /_UAssets/M_Box/__UnrealEngineShader 
- /_UAssets/M_Grid -- (material)
- /_UAssets/M_Grid/__UnrealEngineShader 
- /_UAssets/M_Spike -- (material)
- /_UAssets/M_Spike/__UnrealEngineShader

此外，如果想要获取一个陌生的usd的结构，可以在blender插件中点Get Usd Object，会在列表框里面看到prim结构

### 命令行工具的程序结构

对输入参数的处理 + 使用几何节点对mesh进行处理 + 输出修改的prim到新usd

#### 几何节点接入

现在对于几何节点的处理方法是，使用[NodeToPython插件](https://github.com/BrendanParmer/NodeToPython)，
把几何节点转换成python函数的形式进行调用，**但是这个操作目前不是自动进行，需要手动点击转换按钮进行转换，
并且需要添加对自定义节点的解析支持**

![几何节点](/pic/geonodes.png)

这个几何节点可以转换成[usd_geometrynode.py](/use_geometrynode.py), 
具体的实现方法是给场景中的物体添加一个空的几何节点修改器，然后把usd_geomtrynode.py创建的几何节点树与修改器绑定。
应用修改器，完成对mesh的再次编辑。

**在编辑几何节点时，需要在输出之前添加realise to instance这个节点，不然在应用修改器之后，mesh会消失。**
**另外，一定要应用修改器才能让几何节点的效果实现，否则blender在导出usd时，会忽略未应用的修改器效果。**

在命令行中的修改器应用是自动进行的
```python
obj = bpy.context.scene.objects.get('grid')
modify = obj.modifiers.new(name="MY MDF", type='NODES')
modify.node_group = use_geometrynode.geometry_nodes
bpy.context.view_layer.objects.active = obj  # need to choice the target mesh
print(bpy.ops.object.modifier_apply(modifier='MY MDF'))
```

对于几何节点的管理方法(未实现)，是想参考houdini的python模块，在一个大的class文件夹中，参考ctg_tools。以ctg_tools.NodeGraph
的方式进行调用，这个调用的具体函数是哪个，应该也需要加到命令行参数里面。

#### usd在修改时的元数据问题

在usd工具模块[usdGentookit.py](/usdGenTookit.py)中，已经对usd的upAxis和MetersPerUnit进行了设置，
``` Python
UsdGeom.SetStageUpAxis(source_stage, UsdGeom.GetStageUpAxis(target_stage))
UsdGeom.SetStageMetersPerUnit(source_stage, UsdGeom.GetStageMetersPerUnit(target_stage))
```
但是在prim的替换操作时，**依旧要手动调整UpAxis和MetersPerUnit**

``` Python
# match transform
trans[0][2], trans[0][1] = trans[0][1], trans[0][2]
trans[1][2], trans[1][1] = trans[1][1], trans[1][2]
trans[2][2], trans[2][1] = trans[2][1], trans[2][2]

xformapi = UsdGeom.XformCommonAPI(target_prim)
xformapi.SetRotate(Gf.Vec3f(trans[1][0]- 90, trans[1][1], trans[1][2]))
xformapi.SetScale(Gf.Vec3f(trans[2][0], trans[2][1], trans[2][2])* 0.01)
xformapi.SetTranslate(Gf.Vec3d(trans[0][0], trans[0][1], trans[0][2])* 0.01)
```
这一块的逻辑还是比较混乱，需要再清理一下

