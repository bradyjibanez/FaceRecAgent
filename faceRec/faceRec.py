from imutils import paths
import face_recognition, argparse, pickle, cv2, os, time, sys, glob
from random import randint
import numpy as np

#Used in order to reengage memory encodings. Alternate versioning with integrated networked agents
#could allow for encodings to be saved and updates

def processMemoryEncodings(imagePaths):
	knownEncodings = []
	correspondImage = []
	knownNames = []
	for (i, imagePath) in enumerate(imagePaths):
		name = imagePath.split(os.path.sep)[-2]
		time.sleep(1)
		print("Processing memories of",name,"{}/{}".format(i+1, len(imagePaths)))
		image = cv2.imread(imagePath)
		rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		boxes = face_recognition.face_locations(rgb, model="hog")
		encodings = face_recognition.face_encodings(rgb, boxes)
		for encoding in encodings:
			knownEncodings.append(encoding)
			knownNames.append(name)
	return knownEncodings, knownNames

#Used to produce comparison encodings for unknown encounter images

def produceEncounterEncodings(comparePath, knownEncodings, knownNames):
	encounters = []
	correspondImage = []
	encounterEncodings = []
	print("\n\rProcessing Known Guest Encodings...")

	data = {"encodings": knownEncodings, "names": knownNames}
	f = open("encodings", "wb")
	f.write(pickle.dumps(data))
	f.close()

	print("\n\rLoading Encodings...")
	data = pickle.loads(open("encodings", "rb").read())
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

def findMatches(knownEncodings, encounterEncodings, encounters, data, correspondImage):
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
			except:
				files = glob.glob('/home/brady/Code/AIProject/brainNode/unknown/*')
				for file in files:
					os.remove(file)
				time.sleep(2)
				os.system("clear")
				print("Too many faces in the image to process.")
				sys.exit()
	return names

#Active method to allow for conveying matches to user of new encounter guest to 
#referenced memories

def printMatches(names, encounters, lengthCount, recognizedGuests, checks, knownEncodings):
	i = 0
	samePic = False
	while i != lengthCount:
		if len(names) == 0:
			time.sleep(2)
			os.system("clear")
			print("It appears that the image to reference is not readable. Please try again.")
			#deleteEncounters()
			files = glob.glob('/home/brady/Code/AIProject/brainNode/unknown/*')
			for file in files:
				os.remove(file)
			sys.exit()
		if names[i] != "Unknown":
			checks[i] = 1
			cv2.imshow("This is: "+names[i], encounters[i])
			cv2.waitKey(0)
			cv2.destroyAllWindows()
			newInput = randint(0, 10000000000)
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
				cv2.imwrite(os.path.join(oldMemories, names[i]+str(newInput)+".jpg"), encounters[i])
			recognizedGuests.append(names[i])
		i += 1

#Key method called when unknown guest encounter is provided naming from
#user

def rememberUnknowns(names, encounters, checks):
	count = 0
	for i in checks:
		if i == 0:
			#os.system("clear")
			cv2.imshow("Who is this?: "+names[count], encounters[count])
			cv2.waitKey(0)
			cv2.destroyAllWindows()
			newGuest = input("\n\rWho is in the image I just showed you?")
			confirm = input("\n\rAre you sure this is "+newGuest+"? (y/n)")
			if confirm == "y":
				print("\n\rOK, I'll remember this person as {"+newGuest+"} from now on.")
				os.mkdir('/home/brady/Code/AIProject/brainNode/memory/'+newGuest)
				newMemory = '/home/brady/Code/AIProject/brainNode/memory/'+newGuest
				cv2.imwrite(os.path.join(newMemory, "newPic.jpg"), encounters[count])
			elif confirm == "n":
				tryAgain = input("\n\rIf you would like to enter a new spelling/name, enter {try again}, otherwise, press any key.")
				if tryAgain == "try again":
					newGuest = input("\n\rWho is in the image I just showed you?")
					confirm = input("\n\rAre you sure this is "+newGuest+" ? Press {y} if yes or any key to end this interaction.")
					if confirm == "y":
						print("\n\rOK, I'll remember this person as {"+newGuest+"} from now on.")
						os.mkdir('/home/brady/Code/AIProject/brainNode/memory/'+newGuest)
						newMemory = '/home/brady/Code/AIProject/brainNode/memory/'+newGuest
						cv2.imwrite(os.path.join(newMemory, "newPic.jpg"), encounters[count])
					else:
						print("\n\rThis person will not be remembered.")
				else:
					print("\n\rThis person will not be remembered.")
		count += 1

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

	knownEncodings, knownNames = processMemoryEncodings(imagePaths)
	data, encounterEncodings, encounters, correspondImage = produceEncounterEncodings(comparePath, knownEncodings, knownNames)
	test = 0
	for memory in remembered:
		names = findMatches(knownEncodings, encounterEncodings, encounters, data, correspondImage)
		test += 1
	printMatches(names, encounters, lengthCount, recognizedGuests, checks, knownEncodings)
	rememberUnknowns(names, encounters, checks)
	deleteEncounters()
	return recognizedGuests

print("Processing a new request...")

recognizedGuests = testEncounter()

#Wipes command line output if required.

os.system("clear")

#Prints findings of match method to console (command line)

print("\n\rMATCHES TO KNOWN GUESTS:", recognizedGuests, "\n\r")
