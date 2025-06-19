import os
os.environ['PYOPENGL_PLATFORM'] = 'osmesa'

import trimesh
import pyrender
import numpy as np
tm = trimesh.load('/opt/dmx/jixuanyu/pyrender/examples/models/fuze.obj')
m = pyrender.Mesh.from_trimesh(tm)
# m = pyrender.Mesh.from_trimesh(tm, smooth=False)  #渲染网格时不插值面法线（这对于应该有角度的网格（例如立方体）很有用）
m.primitives
# tms = [trimesh.creation.icosahedron(), trimesh.creation.cylinder(radius=0.5, height=1.0)]  #您还可以从 Trimesh 对象列表中创建单个网格
# m = pyrender.Mesh.from_trimesh(tms)     
print(m.primitives)

#逐面或逐顶点着色
tm.visual.vertex_colors = np.random.uniform(size=tm.vertices.shape) #如果您有一个未纹理的三角形网格，您可以使用每个面或每个顶点的颜色来为其着色：
tm.visual.face_colors = np.random.uniform(size=tm.faces.shape)
m = pyrender.Mesh.from_trimesh(tm)

#实例化
#如果要渲染同一网格的多个不同姿势的副本，可以高效地静态创建大量副本。
#只需将 poses 参数指定为 N 个 4x4 同质变换矩阵的列表，这些矩阵用于确定网格相对于其公共基坐标系的位置：
tfs = np.tile(np.eye(4), (3,1,1))  
#np.eye(4): 创建一个 4x4 的单位矩阵。  #np.tile(..., (3, 1, 1)): 将这个单位矩阵复制3次，并将它们堆叠成一个三维数组。
#(3, ...): 把这张纸复印2份，连同原稿一起，叠成一摞，总共3张。
#(..., 1, 1): 纸张本身的长（行）和宽（列）不要拉伸变形。

tfs[1,:3,3] = [0.1, 0.0, 0.0]    
tfs[2,:3,3] = [0.2, 0.0, 0.0]
#在表达式 M[:3, 3] 中，逗号 , 分隔了不同维度的索引。对于二维矩阵，它的格式是 [行选择器, 列选择器]。把它们合在一起：M[:3, 3] 的意思就是 “请选取第四列中的、属于前三行的那些元素”。

# print(tfs)
m = pyrender.Mesh.from_trimesh(tm, poses=tfs)


#创建点云
#Pyrender 还允许您使用 Mesh.from_points() 静态方法直接从 numpy.ndarray 实例创建包含点云的网格。
#只需提供一个点列表以及可选的每点颜色和法线即可。

pts = tm.vertices.copy()
#tm.vertices 获取3D模型的所有顶点坐标
#.copy() 创建一个副本，避免修改原始数据     
# 从 tm 模型中提取出所有顶点的坐标，并安全地复制一份，存储在 pts 变量中。   
colors = np.random.uniform(size=pts.shape)  
#为点云中的每一个点都创建一个与之对应的、随机的RGB颜色值。    
m = pyrender.Mesh.from_points(pts, colors=colors)  
#这是 pyrender 中一个专门用于从点数据直接创建可渲染网格的类方法 (class method)。  
#这行代码执行后，m 会成为一个 pyrender.Mesh 对象。这个对象可以在之后被添加到 pyrender.Scene 中进行渲染。

#点球
#如果您有一个单色点云，并希望用球体渲染它，您可以通过实例化球形三角网格来渲染它：
sm = trimesh.creation.uv_sphere(radius=0.1)     #使用 trimesh 库创建一个三维的球体模型。radius=0.1: 指定了这个球体模型的半径非常小，只有0.1个单位。
sm.visual.vertex_colors = [1.0, 0.0, 0.0]     #将球体所有顶点的颜色都设置为红色
tfs = np.tile(np.eye(4), (len(pts), 1, 1))    
tfs[:,:3,3] = pts
print(tfs)
m = pyrender.Mesh.from_trimesh(sm, poses=tfs)

#创建灯光  创建灯光很容易——只需指定其基本属性：
#PointLight：点光源，例如灯泡。
#SpotLight：锥形光源，像手电筒一样。
#DirectionalLight：不会随着距离而衰减的普通光。
pl = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=2.0)
sl = pyrender.SpotLight(color=[1.0, 1.0, 1.0], intensity=2.0,innerConeAngle=0.05, outerConeAngle=0.5)
dl = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=2.0)

#创建相机
#Pyrender 支持三种相机类型 - PerspectiveCamera 和 IntrinsicsCamera 类型，它们将场景渲染为人类所见的样子，以及 OrthographicCamera 类型，它们可以保留点之间的距离。
#将摄像机添加到场景时，请确保使用 OpenGL 摄像机坐标系来指定其姿态。简单来说，摄像机的 z 轴指向远离场景的方向，x 轴指向图像空间的右侧，y 轴指向图像空间的上方。
pc = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.414)
#透视摄像机。
# 这种相机模拟人眼的视觉效果，即“近大远小”。平行的线在远离视线时会最终汇聚到远处的“消失点”。这是创建逼真、有深度感的三维场景时最常用的相机。
#yfov=np.pi / 3.0: yfov 指的是垂直方向的视野范围 (Vertical Field of View)。它定义了相机能“看”多宽的角度。
#aspectRatio=1.414: 宽高比，即渲染窗口的 宽度 / 高度。这个参数至关重要，如果设置不正确，渲染出的图像会被压扁或拉伸。1.414 约等于sqrt2，这是一个常见的宽高比。
oc = pyrender.OrthographicCamera(xmag=1.0, ymag=1.0)
#正交相机
#这种相机完全没有透视效果。无论物体距离相机多远，它在屏幕上看起来都一样大。
#xmag 指的是水平方向的放大率。它定义了可视范围宽度的一半。xmag=1.0 意味着相机的可视范围在水平方向上是从 -1.0 到 +1.0，总宽度为 2.0 个单位。
#ymag 指的是垂直方向的放大率。它定义了可视范围高度的一半。

#创建场景
#在渲染任何内容之前，你需要将所有灯光、相机和网格放入场景中。Scene 对象通过将这些图元插入 Node 对象并保存在有向无环图中来跟踪它们的相对姿态。

#添加对象
#要创建场景Scene，只需调用构造函数即可。您可以选择指定环境光颜色和背景颜色：
scene = pyrender.Scene(ambient_light=[0.02, 0.02, 0.02],bg_color=[1.0, 1.0, 1.0])

#您可以通过先创建一个 Node 对象，然后将对象及其姿势添加到该 Node 来将对象添加到场景中。
#姿势被指定为 4x4 同质变换矩阵，存储在节点的 Node.matrix 属性中。
#注意，Node 构造函数要求您指定要添加的是网格、光源还是相机。
mesh = pyrender.Mesh.from_trimesh(tm)
light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=2.0)
cam = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.414)
nm = pyrender.Node(mesh=mesh, matrix=np.eye(4))
nl = pyrender.Node(light=light, matrix=np.eye(4))
nc = pyrender.Node(camera=cam, matrix=np.eye(4))
scene.add_node(nm)
scene.add_node(nl)
scene.add_node(nc)

#您还可以使用 Scene.add() 函数将对象直接添加到场景中，该函数会为您创建节点。
scene.add(mesh, pose=np.eye(4))
scene.add(light, pose=np.eye(4))
scene.add(cam, pose=np.eye(4))

#节点可以是分层的，在这种情况下，节点的 Node.matrix 指定了该节点相对于其父框架的姿势。
#您可以通过在 Scene.add() 或 Scene.add_node() 调用中指定父节点，以分层方式将节点添加到场景中：
scene.add_node(nl, parent_node=nc)
scene.add(cam, parent_node=nm)

#更新对象
#您可以使用 Scene.set_pose() 函数更新现有节点的姿势。只需使用场景中现有的节点以及该节点相对于其父节点的新姿势（4x4 同质变换矩阵）来调用该函数即可：
scene.set_pose(nl, pose=np.eye(4))

#如果要获取节点的局部姿态，可以直接访问其 Node.matrix 属性。但是，如果要获取节点相对于世界坐标系的姿态，可以调用 Scene.get_pose() 方法。
tf = scene.get_pose(nl)

#移除对象
#最后，您可以使用 Scene.remove_node() 函数从场景中删除一个节点及其所有子节点：
scene.remove_node(nl)

#运行渲染器
#适当设置环境变量后，创建场景，然后为 OffscreenRenderer 对象配置窗口宽度、窗口高度和点云点的大小
#然后，只需调用该OffscreenRenderer.render()函数：
r = pyrender.OffscreenRenderer(viewport_width=640,viewport_height=480,point_size=1.0)
color, depth = r.render(scene)

#完成屏幕外渲染器后，您需要关闭它，然后才能运行不同的渲染器或打开同一场景的查看器：
r.delete()  