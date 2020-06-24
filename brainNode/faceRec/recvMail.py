#from itertools import chain
import email, imaplib, os, re

server = 'imap.gmail.com'
port = 993
address = 'shenandoahfacerec@gmail.com'
password = 'waitforme3035'

def findLimboPopIds():
	limboPopulation = os.listdir('/home/brady/Code/AIProject/brainNode/limbo/.')
	for file in limboPopulation:
		string = str(file)
		print(re.findall(r'\d+', string))

def readMail():
	mail = imaplib.IMAP4_SSL(server)
	mail.login(address, password)
	mail.select('"inbox"')

	result, dataFirst = mail.uid('search', None, "ALL")
	if result == 'OK':
		for num in dataFirst[0].split():
			result, data = mail.uid('fetch', num, '(RFC822)')
			if result == 'OK':
				msg = email.message_from_bytes(data[0][1])
				emailSubject = msg['subject']
				emailFrom = msg['from']
				for body in msg.get_payload():
					if body.get_content_type() == 'text/plain':
						emailBody = body.get_payload()
				givenName = emailBody.splitlines()[0]
				limboPopId = matchLimboPopId(emailBody)
				#34 - 37 Deleting referenced email
				mail.store("1:*", '+X-GM-LABELS', '\\Trash')
				mail.expunge()
				mail.close()
				mail.logout()
				return givenName, limboPopId

def matchLimboPopId(emailBody):
	string = str(emailBody)
	limboPopId = re.findall(r'\d+', emailBody.splitlines()[-2])
	if not limboPopId:
		pass
	else:
		return limboPopId[0]

def matchGuestName(emailBody):
	guestName = re.findall(r'\d+', emailBody.splitlines()[-1])
	if not limboPopId:
		pass
	else:
		return limboPopId[0]	





