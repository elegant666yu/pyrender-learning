import os
os.environ["PYOPENGL_PLATFORM"] = "osmesa"   # ← 关键！必须在 import pyrender 前


# import os
# os.environ["PYOPENGL_PLATFORM"] = "egl"   # 指定使用 EGL
# 可选：若多张显卡，固定到编号 0
# os.environ["EGL_DEVICE_INDEX"] = "0"


import numpy as np
import trimesh
import pyrender
import matplotlib.pyplot as plt


# --------- 模型与场景 ---------
fuze_trimesh = trimesh.load('examples/models/fuze.obj')
mesh = pyrender.Mesh.from_trimesh(fuze_trimesh)
scene = pyrender.Scene()
scene.add(mesh)

# 摄像机 & 灯光
camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
s = np.sqrt(2)/2
camera_pose = np.array([
   [0.0, -s,   s,   0.3],
   [1.0,  0.0, 0.0, 0.0],
   [0.0,  s,   s,   0.35],
   [0.0,  0.0, 0.0, 1.0],
])
scene.add(camera, pose=camera_pose)

light = pyrender.SpotLight(color=np.ones(3), intensity=3.0,
                            innerConeAngle=np.pi/16.0,
                            outerConeAngle=np.pi/6.0)
scene.add(light, pose=camera_pose)

# --------- 离屏渲染 ---------
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
plt.show()
plt.tight_layout()
plt.savefig('fuze_render.png', dpi=150)
print('✅ 渲染完成，已保存为 fuze_render.png')