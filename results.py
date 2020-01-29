import requests, base64, time
from bs4 import BeautifulSoup
from twilio.rest import Client

url = 'https://uogstudents.mycampus.gla.ac.uk/psp/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_GRADE.GBL?PORTALPARAM_PTCNAV=HC_SSR_SSENRL_GRADE';

username = input('Type username (example 2399988A): ')
password = input('GUID password: ')

# Your Account Sid and Auth Token from twilio.com/console
ACCOUNT_SID = "";
AUTH_TOKEN = "";
twilio_number = ''

#must start with area code e.g. +448273746221
my_number = '+44'


def getResults():
	url = "https://uogstudents.mycampus.gla.ac.uk/psc/campus/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_GRADE.GBL"

	year = "2019"
	querystring = {"ACAD_CAREER":"UG","INSTITUTION":"GLSGW","STRM":year,"PAGE":"SSR_SSENRL_GRADE"}

	session = requests.Session()
	session.auth = (username, password)

	response = session.get(url, params=querystring)
	soup = BeautifulSoup(response.text,'html.parser')

	results = {}
	resultsTable = soup.find_all("table",{"class":"PSLEVEL1GRIDWBO"})[0] #get table holding results
	trs = resultsTable.find_all("tr")
	del trs[:2] #removes first two rows of the table that are not useful (blank field and collum names)
	for row in trs:
		tds = row.find_all('td')
		counter = 0 
		subject = {} #will hold information regarding each course (course name, credits worth, grade points and GPA)
		courseId = ''
		for el in tds: #for each course 
			if counter == 0:
				courseId = el.text.strip()
			elif counter == 1:
				subject['courseName'] = el.text.strip()
			elif counter == 2:
				subject['credits'] = el.text.strip()
			elif counter == 4:
				subject['grade'] = el.text.strip()
			elif counter == 5:
				subject['gradePoints'] = el.text.strip()
			counter += 1
		results[courseId] = subject

	return results


#function to print results in nice table like on mycampus
def prettyResults(resultsObj):
	gradePoints = 0
	credits = 0
	print('  Course ID  |     Course Name    | Credits | Grade | Grade points')
	for sub,obj in resultsObj.items():
		if obj['gradePoints'] != '':
			credits += float(obj['credits'])
			gradePoints += float(obj['gradePoints'])

		print("{:<12}".format(sub[:12]) + ' | ' + "{:<18}".format(obj['courseName'][:18]) + ' | ' + "{:<7}".format(obj['credits']) + ' | ' + "{:<5}".format(obj['grade']) + ' | ' + obj['gradePoints'])
	if credits != 0:
		print('GPA: ' + str(gradePoints/credits))

#to notify the user of the change in their results
def notify(subject):
	toSend = subject['courseName'] + ' - ' + subject['grade']
	print('Sending SMS: ' + toSend)

	client = Client(ACCOUNT_SID, AUTH_TOKEN)

	message = client.messages.create(
		body=toSend,
	    from_=twilio_number,
	    to=my_number
	    )

def monitor():
	base = getResults()
	while True: #always monitor
		newRes = getResults()
		if newRes != base: #if theres a difference in the data in the new response and old response 
			for sub,obj in newRes.items():
				if base[sub]['grade'] != obj['grade']: #check if the change is in the grade field
					notify(obj)
			base = newRes
		else:
			print('no change...')

		time.sleep(10)

def start():
	print('[1] Monitor for changes in results \n[2] Show me my results and GPA')
	while True:
		choice = input('Type 1 or 2: ')
		if choice == "1":
			monitor()
		elif choice == "2":
			prettyResults(getResults())
			start()
		else:
			continue

start()
