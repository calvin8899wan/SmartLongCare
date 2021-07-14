import os.path as osp
import sys
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from tensorboardX import SummaryWriter
import cv2 
import numpy as np
import matplotlib.pyplot as plt
import json

def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)

this_dir = sys.path[0]
lib_path = osp.join(this_dir,'lib')

add_path(lib_path)
print(sys.path)

from config import cfg
from config import update_config
from utils.transforms import get_affine_transform
from core.inference import get_final_preds

import models

def get_17points(img_path, box=None):
    class Namespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            
    args = Namespace(
        cfg = 'experiments/baseline/res50_384x288_d256x3_adam_lr1e-3.yaml',
        modelDir = '',
        logDir = '',
        dataDir = '',
        opts = ''
    )
    update_config(cfg, args)

    model = eval('models.pose_resnet.get_pose_net')(
        cfg, is_train=False
    )

    model.load_state_dict(torch.load('model/pose_resnet_50_384x288.pth'))
    print('預訓練權重載入完成')

    class ImageLoader():
        def __init__(self, img_path, box):
            self.path = img_path
            self.pixel_std = [200,200]
            self.image_size = [288, 384]
            self.aspect_ratio = self.image_size[0] * 1.0 / self.image_size[1]
            self.box = box
        
        def load(self):
            self.img = cv2.imread(self.path)
            self.center, self.scale = self.box2cs(self.box)
            
            trans = get_affine_transform(self.center[0], self.scale[0], 0, self.image_size)
            reshape_img = cv2.warpAffine(
                self.img,
                trans,
                (int(self.image_size[0]), int(self.image_size[1])),
                flags=cv2.INTER_LINEAR)
            self.reshape_img = reshape_img
        
        def get_tensor(self):
            inp = np.zeros([1,3,384,288])
            _b, _g, _r = self.reshape_img[:,:,0], self.reshape_img[:,:,1], self.reshape_img[:,:,2]
            inp[0,0,:,:] = _r/255
            inp[0,1,:,:] = _g/255
            inp[0,2,:,:] = _b/255
            inp_tensor = torch.tensor(inp, dtype=torch.float32)
            
            return inp_tensor
        
        def box2cs(self, box):
            x, y, w, h = box[:4]
            return self.xywh2cs(x, y, w, h)
        
        def xywh2cs(self, x, y, w, h):
            center = np.zeros((2), dtype=np.float32)
            center[0] = x + w * 0.5
            center[1] = y + h * 0.5

            if w > self.aspect_ratio * h:
                h = w * 1.0 / self.aspect_ratio
            elif w < self.aspect_ratio * h:
                w = h * self.aspect_ratio
            scale = np.array(
                [w * 1.0 / self.pixel_std[0], h * 1.0 / self.pixel_std[1]],
                dtype=np.float32)
            if center[0] != -1:
                scale = scale * 1.25
            
            center = center.reshape([1, 2])
            scale = scale.reshape([1, 2])

            return center, scale

    if osp.exists(img_path):
        img = cv2.imread(img_path)
    else:
        print('無法載入圖片。請重新確認圖片路徑')
        quit()

    if box==None:
        box = [0,0,img.shape[1],img.shape[0]]

    img = ImageLoader(img_path, box)
    img.load()

    inp_tensor = img.get_tensor()
    out_tensor = model(inp_tensor)
    
    heatmap17 = out_tensor.cpu().detach().numpy()
    center, scale = img.center, img.scale
    ans17, score = get_final_preds(cfg, heatmap17, center, scale)

    ans = ans17
    keypoints = {}
    keypoints['pose_keypoints_2d'] = []
    num_joints = ans.shape[1]
    for num in range(num_joints):
        keypoints['pose_keypoints_2d'].append(float(ans[0,num,0]))
        keypoints['pose_keypoints_2d'].append(float(ans[0,num,1]))
        keypoints['pose_keypoints_2d'].append(0.0)

    model_type = 'SampleBaseline'
    out_json = {}
    out_json['type'] = model_type
    out_json['people'] = [keypoints]
    out_json['bbox'] = box

    imgPathSplit = img_path.split(".")[1]
    outFilePath = '.' + imgPathSplit + '.json'
    
    with open(outFilePath, 'w') as file:
        file.write(json.dumps(out_json))
        print('儲存完成')
    
if __name__ == '__main__' :
    get_17points('./data/test.jpg')