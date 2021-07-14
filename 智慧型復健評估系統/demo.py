import sys

from numpy.lib import utils
sys.path.insert(1, './智慧型復健評估系統/pyKinectAzure/')

import numpy as np
from pyKinectAzure.pyKinectAzure import pyKinectAzure, _k4a
import record_tool
from kinectBodyTracker import kinectBodyTracker, _k4abt
import cv2
import time

from utils.utils import Util


# Path to the module
# TODO: Modify with the path containing the k4a.dll from the Azure Kinect SDK
# 修改路徑
modulePath = 'C:\\Program Files\\Azure Kinect SDK v1.4.1\\sdk\\windows-desktop\\amd64\\release\\bin\\k4a.dll' 
bodyTrackingModulePath = 'C:\\Program Files\\Azure Kinect Body Tracking SDK\\sdk\\windows-desktop\\amd64\\release\\bin\\k4abt.dll'
# under x86_64 linux please use r'/usr/lib/x86_64-linux-gnu/libk4a.so'
# In Jetson please use r'/usr/lib/aarch64-linux-gnu/libk4a.so'

# 自訂參數
mode = 'Camera'	# mode(Camera, Record)
exercise_mode = 'Lift_Dumbbells'	# exercise_mode(None, Lift_Dumbbells, Stand_Sit, Knee_up)
side = 'Left'	# 只有在當運動有分左右半身時有效 side(None, Left, Right)
_time = None 	# 遊戲時間(second)


# 系統參數
k = 0
flag = False

if __name__ == "__main__":

	# Initialize the library with the path containing the module
	pyK4A = pyKinectAzure(modulePath)
	recorder = record_tool.load_record(modulePath)
	

	if mode == 'Camera':
		# Open device
		pyK4A.device_open()

		# Modify camera configuration
		device_config = pyK4A.config
		device_config.color_resolution = _k4a.K4A_COLOR_RESOLUTION_720P	# _k4a.K4A_COLOR_RESOLUTION_720P、K4A_COLOR_RESOLUTION_1536P、_k4a.K4A_COLOR_RESOLUTION_OFF
		device_config.depth_mode = _k4a.K4A_DEPTH_MODE_NFOV_UNBINNED
		# print(device_config)

		width, height = 1280, 720

		# Start cameras using modified configuration
		pyK4A.device_start_cameras(device_config)

		# Initialize the body tracker
		pyK4A.bodyTracker_start(bodyTrackingModulePath)

	elif mode == 'Record':

		file_PATH = './recording/test01.mkv'

		# Open record
		recorder.playback_open(file_PATH)

		width, height = 512, 512

		# Initialize the body tracker
		pyK4A.record_bodyTracker_start(bodyTrackingModulePath, recorder.playback_get_calibration())


	# 初始化工具
	util = Util(width, height)	
	util.set_exercise(exercise_mode, side)

	while True:
		# Frame start time
		frame_start = time.time()

		if mode == 'Camera':

			# Get capture
			pyK4A.device_get_capture()

			# Get the depth image from the capture
			depth_image_handle = pyK4A.capture_get_depth_image()

			# Get the color image from the capture
			color_image_handle = pyK4A.capture_get_color_image()

		elif mode == 'Record':

			# Get capture
			pyK4A.capture_handle = recorder.get_capture()

			# 確認是否還有下一幀
			if pyK4A.capture_handle:
				# Get the depth image from the capture
				depth_image_handle = recorder.capture_get_depth_image()


		# Check the image has been read correctly
		if color_image_handle:

			# Perform body detection
			pyK4A.bodyTracker_update()

			# Read and convert the image data to numpy array:
			color_image = pyK4A.image_convert_to_numpy(color_image_handle)


			# body_image_color 屬於深度影像大小，無法校正至 RGB 影像
			# Read and convert the image data to numpy array:
			# 將深度圖像轉換為RGB三通道，用於可視化
			# depth_image = pyK4A.image_convert_to_numpy(depth_image_handle)
			# depth_color_image = cv2.convertScaleAbs (depth_image, alpha=0.05)  #alpha is fitted by visual comparison with Azure k4aviewer results 
			# depth_color_image = cv2.cvtColor(depth_color_image, cv2.COLOR_GRAY2RGB) 

			# Get body segmentation image
			# body_image_color = pyK4A.bodyTracker_get_body_segmentation()

			# 按比例重疊深度圖像與人體區塊圖像
			# util.combined_image = cv2.addWeighted(depth_color_image, 0.8, body_image_color, 0.2, 0)

			util.combined_image = color_image
			
			# 顯示運動名稱
			util.put_text_in_center((util.width/2, 50), exercise_mode, 0.7, (0, 255, 0), 1)


			# 偵測到人後倒數3秒鐘進入遊戲
			if not util.game_start:
				if flag or len(pyK4A.body_tracker.bodiesNow) != 0:	
					flag = True			
					game_start = util.game_ready()

			else:
				# 於畫面中顯示遊戲狀態  
				util.show_info()	
				if not util.game_stop:
					# Draw the skeleton
					for body in pyK4A.body_tracker.bodiesNow:	# 遍覽畫面中出現的目標
						# 若想投影到 RGB 影像上要寫 skeleton2D = pyK4A.bodyTracker_project_skeleton(body.skeleton,  _k4a.K4A_CALIBRATION_TYPE_COLOR)	
						# 投影到深度影像則 skeleton2D = pyK4A.bodyTracker_project_skeleton(body.skeleton)	
						skeleton2D = pyK4A.bodyTracker_project_skeleton(body.skeleton,  dest_camera=_k4a.K4A_CALIBRATION_TYPE_COLOR)	
						util.combined_image = pyK4A.body_tracker.draw2DSkeleton(skeleton2D, body.id, util.combined_image)
						# 取得3維關節座標
						skeleton3D = pyK4A.bodyTracker_3Dskeleton(body.skeleton)						
						# 更新骨架資訊
						util.update(skeleton2D, skeleton3D)
						# 計算動作完成次數
						util.cal_exercise()
						break # 只計算畫面中的其中一人
				else:
					util.put_text_in_center((int(util.width/2), int(util.height/2-20)), 'Time\'s up!', 1.5, (0, 0, 255), 2)
					

			# Frame end time
			frame_end = time.time()
			# Show FPS
			cv2.putText(util.combined_image, 'FPS:{:.1f}'.format(1/(frame_end-frame_start)), (15, 40), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1, cv2.LINE_AA)

			# Overlay body segmentation on depth image
			cv2.imshow('Segmented Depth Image', util.combined_image)
			k = cv2.waitKey(1)

			# Release the image
			pyK4A.image_release(depth_image_handle)
			pyK4A.image_release(color_image_handle)
			pyK4A.image_release(pyK4A.body_tracker.segmented_body_img)

		pyK4A.capture_release()
		pyK4A.body_tracker.release_frame()

		if k==27:    # Esc key to stop
			break
		elif k == ord('q'):
			cv2.imwrite('outputImage.jpg', util.combined_image)


	if mode == 'camera':
		pyK4A.device_stop_cameras()
		pyK4A.device_close()
	elif mode == 'record':
		recorder.playback_close()