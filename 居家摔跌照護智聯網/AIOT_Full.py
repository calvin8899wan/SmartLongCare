import cv2
import tensorflow as tf
import numpy as np
import os, sys
import requests
import time

from pathlib import Path
from tensorflow import keras
from os import listdir
from os.path import isfile, join
from keras.preprocessing import image
from PIL import Image
from datetime import datetime

mmwavemodel = keras.models.load_model('mmwave.h5')
mobilenetmodel = keras.models.load_model('mobilenet.h5')

def Line_Notify(token, message, img):
    #設定群組對應的權杖
 headers = {"Authorization": "Bearer " + token}
    #填入想傳送的訊息
 param = {'message': message}
    #上傳想要傳送的圖片
 image = {'imageFile' : open(str(img), 'rb')}
    #傳送
 r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = param, files = image)
 return r.status_code

def mmwave(num):
 img = image.load_img("/home/dsdl/Desktop/AIOT/image_data/test/" + num + ".jpg",target_size=(150,150))
 x = np.array(img)
 x = np.expand_dims(x, axis=0)

 images = np.vstack([x])
 classes = mmwavemodel.predict_classes(images, batch_size=10)
 classes = classes[0][0]
    
 if classes == 0:
  print('null')
 else:
  print('people')

def load_image(img_path, show=False):
 img = image.load_img(img_path, target_size=(150, 150))
 img_tensor = np.array(img)
 img_tensor = np.expand_dims(img_tensor, axis=0)                                               

 if show:
  plt.imshow(img_tensor[0])                           
  plt.axis('off')
  plt.show()

 return img_tensor

try:
 while True:
  select = eval(input(""))
  if (select == 0) or (select == 1):
   mmwave(str(select))
  elif (select == 2) or (select == 3):
   mmwave(str(select))

   cap = cv2.VideoCapture(0)
   if not cap.isOpened():
    print("Cannot open camera")

   ret, frame = cap.read()

   now = datetime.now()

   month = now.strftime("%m-")
   day = now.strftime("%d-")
   time = now.strftime("%H-%M-%S")


   cv2.imwrite("/home/dsdl/Desktop/AIOT/photos/"+month + day+time+".png",frame)
   Imagefile = "/home/dsdl/Desktop/AIOT/photos/"+month + day+time+".png"
   new_image = load_image(Imagefile)
   print(Imagefile)
   pred = mobilenetmodel.predict(new_image)
   value = pred.tolist()
   print(value)
   number=value[0]
   tmp = max(number)
   index = number.index(tmp)
   print(index)
   if index == 0:
    Line_Notify('EhuX3XFfxeNoRUDoUV0EnYTgasyQScGfZjOyTrB9FYR','跌倒！偵測到跌倒事件，請參照照片，並儘速與跌倒者聯繫。',Imagefile)
   cv2.waitKey(0)
   cap.release()
   cv2.destroyAllWindows()
  else:
   print("again")
except KeyboardInterrupt:
 print('關閉程式')

