import smtplib, ssl, os, glob
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

def send_match(guest):

	smtpServer = "smtp.gmail.com"
	port = 465
	password = "waitforme3035"
	senderEmail = "shenandoahFaceRec@gmail.com"
	receiverEmail = "bradyjibanez@gmail.com"
	files = glob.glob('/home/brady/Code/AIProject/brainNode/encounterImages/capture.jpg')
	for file in files:
		newEncounter = open(file, 'rb').read()

	message = MIMEMultipart("alternative")
	message["Subject"] = "A known guest has been seen"
	message["From"] = senderEmail
	message["To"] = receiverEmail
	knownGuest = guest
	text = "I see "+ knownGuest +" is near me."
	text = MIMEText(text, "plain")
	match = MIMEImage(newEncounter)
	match.add_header('Content-Disposition', "attachment; filename= %s" % guest)
	message.attach(match)
	message.attach(text)

	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(smtpServer, port, context=context) as server:
		server.login(senderEmail, password)
		server.sendmail(senderEmail, receiverEmail, str(message))

def make_memory(count):
	count += 1
	smtpServer = "smtp.gmail.com"
	port = 465
	password = "waitforme3035"
	senderEmail = "shenandoahFaceRec@gmail.com"
	receiverEmail = "bradyjibanez@gmail.com"
	files = glob.glob('/home/brady/Code/AIProject/brainNode/unknown/*')
	for file in files:
		print(file)
		newEncounter = open(file, 'rb').read()

	message = MIMEMultipart("alternative")
	message["Subject"] = "Someone new has appeared"
	message["From"] = senderEmail
	message["To"] = receiverEmail
	text = "Who is this? \n\nTo add them as known guest "+str(count)+" please reply with their full name or send 'no' to remove them."
	text = MIMEText(text, "plain")
	unknown = MIMEImage(newEncounter)
	seenPerson = "unknown"
	message.add_header('Content-Disposition', "attachment; filename= %s" % seenPerson)
	message.attach(text)
	message.attach(unknown)

	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(smtpServer, port, context=context) as server:
		server.login(senderEmail, password)
		server.sendmail(senderEmail, receiverEmail, str(message))

