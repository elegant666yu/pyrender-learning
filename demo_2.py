import os
os.environ["PYOPENGL_PLATFORM"] = "osmesa"

import numpy as np
import trimesh
import pyrender
import matplotlib.pyplot as plt

bunny_trimesh = trimesh.load('/opt/dmx/jixuanyu/pyrender/examples/models/bunny.ply')
mesh = pyrender.Mesh.from_trimesh(bunny_trimesh, smooth=False)
scene = pyrender.Scene(ambient_light=[0.3, 0.3, 0.3])
scene.add(mesh)

camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
# s = np.sqrt(2)/2
# camera_pose = np.array([
#    [0.0, -s,   s,   0.3],
#    [1.0,  0.0, 0.0, 0.0],
#    [0.0,  s,   s,   0.35],
#    [0.0,  0.0, 0.0, 1.0],
# ])
#相机 —— 简单地放到模型前方 size*2 的位置
bbox_min, bbox_max = bunny_trimesh.bounds
model_size = np.linalg.norm(bbox_max - bbox_min)
camera_pose = np.eye(4)
camera_pose[2, 3] = model_size * 2.0   # z 轴正向拉远
scene.add(camera, pose=camera_pose)

light = pyrender.SpotLight(color=np.ones(3), intensity=3.0,
                            innerConeAngle=np.pi/16.0,
                            outerConeAngle=np.pi/6.0)
scene.add(light, pose=camera_pose)

r = pyrender.OffscreenRenderer(400, 400)
color, depth = r.render(scene)
r.delete()                # 记得释放资源

plt.figure()
plt.subplot(1,2,1)
plt.axis('off')
plt.imshow(color)
plt.subplot(1,2,2)
plt.axis('off')
plt.imshow(depth, cmap=plt.cm.gray_r)
plt.tight_layout()
plt.savefig('bunny_render.png', dpi=150)
plt.show()
print('✅ 渲染完成，已保存为 bunny_render.png')