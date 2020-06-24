from imutils import paths
import face_recognition, argparse, pickle, cv2, os, time, sys, glob, datetime
from multiprocessing import Process
import numpy as np
from sendMail import send_match, make_memory
from recvMail import readMail
#from processMemoryEncodings import processMemoryEncodings

#Used in order to reengage memory encodings. Run as subprocess to save time in returning output
def processMemoryEncodings(imagePaths):
	knownEncodings = []
	correspondImage = []
	knownNames = []
	for (i, imagePath) in enumerate(imagePaths):
		name = imagePath.split(os.path.sep)[-2]
		#Used for testing run time execution
		#print("Processing memories of",name,"{}/{}".format(i+1, len(imagePaths)))
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

#Used to produce comparison encodings for unknown encounter images
def produceEncounterEncodings(comparePath):
	encounters = []
	correspondImage = []
	encounterEncodings = []
	print("\n\rProcessing Known Guest Encodings...")
	print("\n\rLoading Encodings...")

	knownEncodings = pickle.loads(open("/home/brady/Code/AIProject/brainNode/faceRec/encodings", "rb").read())
	knownNames = pickle.loads(open("/home/brady/Code/AIProject/brainNode/faceRec/names", "rb").read())
	data = {"encodings": knownEncodings, "names": knownNames}
	for (j, comparison) in enumerate(comparePath):
		print("Processing new encounter {}/{}".format(j+1, len(comparePath)))
		image = cv2.imread(comparison)
		encounters.append(image)
		rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		boxes = face_recognition.face_locations(rgb, model="hog")
		encounterEncoding = face_recognition.face_encodings(rgb, boxes)
		for encoding in encounterEncoding:
			encounterEncodings.append(encounterEncoding)
			correspondImage.append(image)	
	return data, encounterEncodings, encounters, correspondImage

#Active comparison is produced here between new encounter encoding and generated
#memory image encodings
def findMatches(encounterEncodings, encounters, data, correspondImage):
	names = []
	counts = None
	count = 0
	name = None

	print("Finding Matches...")

	for encounterEncoding in encounterEncodings:
		try:
			matches = face_recognition.compare_faces(data["encodings"], np.array(encounterEncoding))
			name = "Unknown"
			if True in matches:
				matchedIdxs = [j for (j, b) in enumerate(matches) if b]
				counts = {}
				for i in matchedIdxs:
					name = data["names"][i]
					counts[name] = counts.get(name, count+1)
					count += 1
				name = max(counts, key=counts.get)
			names.append(name)
		except Exception as e:
			files = glob.glob('/home/brady/Code/AIProject/brainNode/unknown/*')
			for file in files:
				os.remove(file)
			msg = "ERROR: Too many faces in the image to process."
			print(e)
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			with open("/home/brady/Code/AIProject/brainNode/faceRec/log.txt", "a") as log:
				log.write("\n"+msg+" @ "+str( datetime.datetime.now()))
			sys.exit()
	return names

#Active method to allow for conveying matches to user of new encounter guest to
#referenced memories
def printMatches(names, encounters, lengthCount, recognizedGuests, checks):
	i = 0
	samePic = False
	while i != lengthCount:
		if len(names) == 0:
			msg = "ERROR: brainNode could not see a face in that image."
			print(msg)
			with open("/home/brady/Code/AIProject/brainNode/faceRec/log.txt", "a") as log:
				log.write("\n"+msg+" @ "+str( datetime.datetime.now()))
			deleteEncounters()
			files = glob.glob('/home/brady/Code/AIProject/brainNode/unknown/*')
			unknowns = []
			for file in files:
				unknowns.append(file)
				os.remove(file)
			sys.exit()
		if names[i] != "Unknown":
			checks[i] = 1
			send_match(names[i])
			newMemoryNumber = len(os.listdir('/home/brady/Code/AIProject/brainNode/memory/'+names[i]))+1
			oldMemories = '/home/brady/Code/AIProject/brainNode/memory/'+names[i]
			newEncounters = list(paths.list_images('/home/brady/Code/AIProject/brainNode/unknown/'))
			for encounter in newEncounters:
				encounter = cv2.resize(cv2.imread(encounter), (224, 224)).astype(np.float32)
				for image in list(paths.list_images(oldMemories)):
					image = cv2.resize(cv2.imread(image), (224, 224)).astype(np.float32)
					difference = cv2.subtract(image, encounter)
					result = not np.any(difference)
					if result is True:
						samePic = True
			if samePic == False:
				#This is what creates new memories for already known guests
				cv2.imwrite(os.path.join(oldMemories, names[i]+str(newMemoryNumber)+".jpg"), encounters[i])
				#Delete unknowns here when dealt with
				deleteEncounters()
			recognizedGuests.append(names[i])
		elif names[i] == "Unknown":
			#These references to memory are just for known guest counts thus far
			make_memory(len(os.listdir('/home/brady/Code/AIProject/brainNode/memory/.')))
			nextKnown = len(os.listdir('/home/brady/Code/AIProject/brainNode/memory/.'))+1
			msg = "Waiting for response to deal with seen unknown guest."
			print(msg)
			with open("/home/brady/Code/AIProject/brainNode/faceRec/log.txt", "a") as log:
				log.write("\n"+msg+" @ "+str( datetime.datetime.now()))
			files = glob.glob("/home/brady/Code/AIProject/brainNode/unknown/*")
			for file in files:
				os.rename(file, "/home/brady/Code/AIProject/brainNode/limbo/limbo"+str(nextKnown)+".jpg")
			numUnknowns = len(glob.glob('/home/brady/Code/AIProject/brainNode/limbo/.'))
		i += 1

#Used to remove encounters from unknown reference space. Even if user never identifies
#an unknown, no need to hold the reference since only convolutes processing time
#for subsequent encounters
def deleteEncounters():
	comparePath = list(paths.list_images("/home/brady/Code/AIProject/brainNode/unknown/"))
	for image in comparePath:
		try:
			if os.path.isfile(image):
				os.unlink(image)
		except Exception:
			pass

#Method to engage all required methods for facial recognition of the learning
#brain agent
def testEncounter():
	guests = []
	recognizedGuests = []
	imagePaths = list(paths.list_images("/home/brady/Code/AIProject/brainNode/memory/"))
	comparePath = list(paths.list_images("/home/brady/Code/AIProject/brainNode/unknown/"))
	remembered = os.listdir('/home/brady/Code/AIProject/brainNode/memory/')
	count = 0
	for x in os.listdir('/home/brady/Code/AIProject/brainNode/unknown/'):
		count += 1
	lengthCount = count
	checks = []
	for i in range(0, lengthCount):
		checks.append(0)

	print("\n\rKnown Guests:", remembered)
	#Updates encodings while letting everything else run more efficiently time-wise
	#Was done as subprocess, but now as multiprocess (sub for non python script, multi for within same python script)
	#SUBPROCESS OUTSIDE OF THIS SCRIPT, MULTI INSIDE
	#subprocess.call(processMemoryEncodings())
	#updateEncoding = Process(target=processMemoryEncodings(imagePaths))
	#updateEncoding.start()
	data, encounterEncodings, encounters, correspondImage = produceEncounterEncodings(comparePath)
	test = 0
	for memory in remembered:
		names = findMatches(encounterEncodings, encounters, data, correspondImage)
		test += 1
	printMatches(names, encounters, lengthCount, recognizedGuests, checks)
	return recognizedGuests

print("Processing a new request...")

recognizedGuests = testEncounter()

msg = ("MATCH TO KNOWN GUESTS: "+str(recognizedGuests))
if recognizedGuests[0] != None:
	print(msg)
	#Updates log...same anywhere else seen above
	with open("/home/brady/Code/AIProject/brainNode/faceRec/log.txt", "a") as log:
		log.write("\n"+msg+" @ "+str( datetime.datetime.now()))