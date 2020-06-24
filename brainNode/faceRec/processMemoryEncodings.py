from imutils import paths
from datetime import datetime
import os, cv2, face_recognition, pickle, time

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

#Used to accelerate encoding for first run and if exception
breakPoint = 5

while True:
	count = 0
	while True:
		time.sleep(1)
		count += 1
		print(count, " second(s)")
		if count == breakPoint:
			try:
				processMemoryEncodings(imagePaths)
				breakPoint = 1200
				break
			except Exception as e:
				print("Encodings not rendered due to error.")
				breakPoint = 5
				break
		else:
			pass