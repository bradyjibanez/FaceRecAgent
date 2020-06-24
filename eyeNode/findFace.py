from imutils import paths
import numpy as np
import argparse
import imutils
import pickle
import cv2
import os, time, picamera, io

def find():
	stream = io.BytesIO()
	with picamera.PiCamera() as camera:
		camera.resolution = (320, 240)
		camera.capture(stream, format='jpeg')

	buff = np.fromstring(stream.getvalue(), dtype=np.uint8)

	image = cv2.imdecode(buff, 1)

	cascade = cv2.CascadeClassifier("/home/pi/opencv-3.0.0/cascades/haarcascade_frontalface_default.xml")

	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	faces = cascade.detectMultiScale(gray, 1.1, 5)

	print("Found "+str(len(faces))+" face(s)")

	for (x,y,w,h) in faces:
		cv2.rectangle(image,(x,y),(x+w,y+h),(255,255,0),2)

	if len(faces) > 0:
		return image


