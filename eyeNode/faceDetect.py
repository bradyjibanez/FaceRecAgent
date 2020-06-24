import cv2, face_recognition, os, time
import numpy as np
from findFace import find

count = 1
while True:
	face = find()
	try:
		if face is not None:
			print("face found")
			cv2.imwrite("face.jpg", face)
			os.system("scp face.jpg brady@99.232.132.147:/home/brady/Documents/FACE/theImage"+str(count)+".jpg")
			count += 1
			time.sleep(2)
	except FileNotFoundError:
		print("no face found")
		time.sleep(2)

