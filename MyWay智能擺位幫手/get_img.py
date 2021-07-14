import cv2
import datetime
from CPU17 import get_17points

def get_img():
    datetime_now = datetime.datetime.now()
    time = datetime.datetime.now().replace(microsecond=0)  + datetime.timedelta(hours=+8)
    time_s = str(time)
    time_s = time_s.replace("-","-")
    time_s = time_s.replace(":","_")
    print(time_s)

    cam = cv2.VideoCapture(0)

    ret, img = cam.read()
    if ret:
        cv2.imwrite('./data/%s.jpg'%(time_s), img)
        print('已拍到照片')
    else:
        print('沒有抓到攝像頭')

    cam.release()
    cv2.destroyAllWindows()
    get_17points('./data/%s.jpg'%(time_s))

get_img()