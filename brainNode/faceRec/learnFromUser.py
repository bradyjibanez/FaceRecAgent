from imutils import paths
import face_recognition, argparse, pickle, cv2, os, time, sys, glob, datetime, pathlib
from random import randint
import numpy as np
from sendMail import send_match, make_memory
from recvMail import *

def learnFromUserInput():
	numUnknowns = len(glob.glob('/home/brady/Code/AIProject/brainNode/limbo/.'))
	try:
		valid = "False"
		#Blank assignment for error handling
		newGuest = None
		newGuest, limboCount = readMail()
		memory = glob.glob("/home/brady/Code/AIProject/brainNode/memory/*/")
		files = glob.glob('/home/brady/Code/AIProject/brainNode/limbo/*')
		#Remove encounter as not to be saved to memory as per user request
		if (newGuest == "No") or (newGuest == "no"):
			for file in files:
				if file == ('/home/brady/Code/AIProject/brainNode/limbo/limbo'+limboCount+'.jpg'):
					msg = ("A seen unknown guest was discarded from memory.")
					with open("/home/brady/Code/AIProject/brainNode/faceRec/log.txt", "a") as log:
						log.write("\n"+msg+" @ "+str( datetime.datetime.now()))
					os.remove(file)
			return valid, newGuest
		#Save new encounter as known guest or correct messup to redirect encounter to existing guest memory
		else:
			#Check if guest is already known and add this encounter to memory for better encoding
			for file in memory:
				name = pathlib.PurePath(file).name
				print("FILE, NAME: ", file, name)
				if newGuest == name:
					img = cv2.imread('/home/brady/Code/AIProject/brainNode/limbo/limbo'+limboCount+'.jpg')
					sameGuest = file
					newMemoryNumber = len(os.listdir('/home/brady/Code/AIProject/brainNode/memory/'+name+'/'))+1
					cv2.imwrite(os.path.join(sameGuest, name+newMemoryNumber+'.jpg'), img)
					print(name+newMemoryNumber+'.jpg')
					for file in files:
						if file == ('/home/brady/Code/AIProject/brainNode/limbo/limbo'+limboCount+'.jpg'):
							cv2.imwrite(os.path.join(newMemory, "firstEncounter.jpg"), img)
							os.remove(file)
					valid = "True"
					return valid, newGuest
			#Save new encounter in memory under newguest directory
			os.mkdir('/home/brady/Code/AIProject/brainNode/memory/'+newGuest)
			newMemory = '/home/brady/Code/AIProject/brainNode/memory/'+newGuest
			img = cv2.imread('/home/brady/Code/AIProject/brainNode/limbo/limbo'+limboCount+'.jpg')
			for file in files:
				if file == ('/home/brady/Code/AIProject/brainNode/limbo/limbo'+limboCount+'.jpg'):
						cv2.imwrite(os.path.join(newMemory, "firstEncounter.jpg"), img)
						os.remove(file)
			valid = "True"
			return valid, newGuest

	except Exception as e:
		return valid, newGuest

imagePaths = list(paths.list_images("/home/brady/Code/AIProject/brainNode/memory/"))

def processMemoryEncodings(imagePaths):
	knownEncodings = []
	correspondImage = []
	knownNames = []
	for (i, imagePath) in enumerate(imagePaths):
		name = imagePath.split(os.path.sep)[-2]
		#Used for testing run time execution
		print("Processing memories of",name,"{}/{}".format(i+1, len(imagePaths)))
		image = cv2.imread(imagePath)
		rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		boxes = face_recognition.face_locations(rgb, model="hog")
		encodings = face_recognition.face_encodings(rgb, boxes)
		for encoding in encodings:
			knownEncodings.append(encoding)
			knownNames.append(name)
	#Keeps memory encodings of imgs and names for quick subsequent reference upon later call
	encodings = open("/home/brady/Code/AIProject/brainNode/faceRec/encodings", "wb")
	encodings.write(pickle.dumps(knownEncodings))
	encodings.close()
	names = open("/home/brady/Code/AIProject/brainNode/faceRec/names", "wb")
	names.write(pickle.dumps(knownNames))
	names.close()	

while True:
	time.sleep(5)
	learning, newGuest = learnFromUserInput()
	if learning == "True":
		msg = ("New guest "+newGuest+" was saved to memory.")
		print(msg)
		with open("/home/brady/Code/AIProject/brainNode/faceRec/log.txt", "a") as log:
			log.write("\n"+msg+" @ "+str( datetime.datetime.now()))
		processMemoryEncodings(imagePaths)
	else:
		print("Nothing learned.")