#Auth
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

#Email
import base64
from email.mime.text import MIMEText
from string import Template

#Calendar
from datetime import datetime, timedelta
from pytz import timezone
import json

#APIclient
from apiclient import errors

#USER VARIABLES
from config import * # (DON'T DO THIS IN PRODUCTION-GRADE CODE)

def createTemplates():
	"""Create email Template objects"""
	
	msg_template = ""
	with open(PATH_TO_MSG_TEMPLATE) as file:
		msg_template = Template(file.read())
		
	subject_template = Template(SUBJECT_TEMPLATE)
	
	return (msg_template, subject_template)


def CreateMessage(sender, to, subject, message_text, cc='', bcc=''):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
	cc: Email address(es) of CC (Optional)
	bcc: Email address(es) of BCC (Optional)

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text, 'html')
  message['to'] = to
  message['cc'] = cc
  message['bcc'] = bcc
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

def SendMessage(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message).execute())
    print ('Message Id: %s' % message['id'])
    return message
  except errors.HttpError as error:
    print ('An error occurred: %s' % error)

# Google API Permissions
SCOPES = ['https://www.googleapis.com/auth/gmail.send', #Gmail - send
			'https://www.googleapis.com/auth/calendar.readonly', #Calendar - read-only
			'https://www.googleapis.com/auth/spreadsheets.readonly'] #Sheets - read-only

def auth():
	"""Authenticate into Google API services"""
	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				'credentials.json', SCOPES)
			#flow.user_agent = APPLICATION_NAME
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)
	
	return creds


def main():
	creds = auth()
	
	msg_template, subject_template = createTemplates()
	
	# Build google services
	gmail_svc = build('gmail', 'v1', credentials=creds)
	calendar_svc = build('calendar', 'v3', credentials=creds)
	sheets_svc = build('sheets', 'v4', credentials=creds)
	
	# Retrieve Calendar events
	now = datetime.now(timezone(TUTOR_TIMEZONE))
	next_day_start = now.replace(hour=0, minute=0, second=0, microsecond=0) # Reset to start of today
	if (now.time().isoformat() > NIGHTLY_CUTOFF):
		next_day_start += timedelta(hours=24) # Get next calendar day
	next_day_end = next_day_start + timedelta(hours=24)
	
	# Get next day's events
	events_result = calendar_svc.events().list(calendarId='primary', timeMin=next_day_start.isoformat(),
												timeMax=next_day_end.isoformat(),
												singleEvents=True, orderBy='startTime').execute()
	events = events_result.get('items', [])
	
	tutoring_events = []
	if not events:
		print('No upcoming events on calendar.')
	for event in events:
		# Ensure Trilogy bootcamp session
		if EVENT_DESCRIPTION not in event.get('description', ''):
			#print(f"Not bootcamp session: {event['summary']}")
			continue
		# Check for cancellation
		if 'Canceled' in event.get('summary', ''):
			#print(f"Cancelled: {event['summary']}")
			continue
		tutoring_events.append(event)
		
	if not tutoring_events:
		print('No upcoming tutoring sessions found.')
		return
	
	#Retrieve timezone from Sheets
	sheet = sheets_svc.spreadsheets()
	result = sheet.values().get(spreadsheetId=SHEET_NAME, range=RANGE_NAME).execute()
	values = result.get('values', [])
	
	student_data = {}
	if not values:
		print("No Sheets data found. Check your RANGE_NAME to ensure you're looking in the right place in your Sheet.")
	else:
		for row in values:
			try:
				student_data[row[EMAIL_COLUMN]] = (row[NAME_COLUMN], row[TZ_COLUMN], row[ZOOM_COLUMN])
			except: #TODO: IndexError? TypeError? Catch & return error message
				print('If range out of index error, ensure there is data in each of the columns above for each student!')
	
	# Optionally check for emails already sent for next day
	already_sent = []
	if not RESENDING_EMAILS and not IS_IN_TEST_MODE:
		if os.path.exists('db.json'):
			with open('db.json', 'r') as sent_file:
				sent_dict = json.load(sent_file)
				already_sent = sent_dict.get(next_day_start.isoformat(), [])
				
	
	# Send confirmation email for each event
	messages_sent = []
	for event in tutoring_events:
		if event['id'] not in already_sent:
			student_email = ""
			for attendee in event['attendees']:
				if attendee['email'] != TUTOR_EMAIL: # 2 attendees, ignore tutor
					student_email = attendee['email']
			#Lookup email in Sheets data
			while student_email != 'skip' and student_email not in student_data:
				print(f"Email {student_email} not found. If you know who this is, please supply the email address they registered with or enter 'skip' to skip to the next session.")
				student_email = input()
			if student_email == 'skip':
				continue
			
			#Get first name and timezone offset
			student_name = student_data[student_email][0]
			student_tz = student_data[student_email][1]
			student_zoom = student_data[student_email][2] #TODO: Test to ensure value?
			
			student_firstname = student_name.split(' ')[0]
			
			tz = ""	
			if 'CST' in student_tz:
				tz = timezone('US/Central')
			elif 'EST' in student_tz:
				tz = timezone('US/Eastern')
			elif 'MST' in student_tz:
				tz = timezone('US/Mountain')
			elif 'PST' in student_tz:
				tz = timezone('US/Pacific')
			else:
				print(f"Unable to interpret timezone. Please enter the timezone for {student_name} in pytz format (https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568).")
				tz = timezone(input())
			
			
			event_start_raw = event['start'].get('dateTime', event['start'].get('date'))
			event_start_dt = datetime.strptime(event_start_raw, '%Y-%m-%dT%H:%M:%S%z').astimezone(tz)
			event_end_dt = event_start_dt + timedelta(minutes=50)
			
			event_date = event_start_dt.strftime('%A, %B %d')
			event_start = event_start_dt.strftime('%I:%M')
			event_end = event_end_dt.strftime('%I:%M%p %Z')
			
			msg_text = msg_template.substitute(name=student_firstname,
							date=event_date, starttime=event_start, endtime=event_end, zoomlink=student_zoom)
			
			subject_text = subject_template.substitute(date=event_date, starttime=event_start, endtime=event_end)
		
			message = None
			if IS_IN_TEST_MODE:
				message = CreateMessage(sender=TUTOR_SENDER, to=TEST_EMAIL, subject=subject_text, message_text=msg_text)
			else:
				message = CreateMessage(sender=TUTOR_SENDER, to=student_email, subject=subject_text, message_text=msg_text, cc='centraltutorsupport@bootcampspot.com')
				
			SendMessage(gmail_svc, 'me', message)
			messages_sent.append(event['id'])
	
	if not messages_sent:
		print(f"All confirmation emails for next day ({len(already_sent)}) already sent! (RESENDING_EMAILS = FALSE)")
	else:
		print(f"Emails sent: {len(messages_sent)}, emails skipped because already sent: {len(already_sent)}.")
	
	if not IS_IN_TEST_MODE:
		next_day_str = next_day_start.isoformat()
		sent_dict = {}
		if os.path.exists('db.json'):
			with open('db.json', 'r') as sent_file:
				sent_dict = json.load(sent_file)
				day_msgs = sent_dict.get(next_day_str, [])
				set_day_msgs = set(day_msgs)
				set_day_msgs.update(messages_sent)
				sent_dict[next_day_str] = list(set_day_msgs) #List -> set -> list, there has to be a better way....
				
				for date in sent_dict:
					if date != next_day_str:
						del sent_dict[date] # Purge old keys
		else:
			sent_dict[next_day_str] = messages_sent
			
		with open('db.json', 'w') as sent_file:
			json.dump(sent_dict, sent_file)
	
	if IS_IN_TEST_MODE:
		print('Test complete. Set IS_IN_TEST_MODE = False in config.py to send to students.')
	
if __name__ == "__main__":
	main()