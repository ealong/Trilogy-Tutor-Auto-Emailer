PATH_TO_MSG_TEMPLATE = #String - file path to msg_template.html
SUBJECT_TEMPLATE = #String - desired subject line containing the placeholder variables $date, $starttime, and $endtime
"""
Example:

SUBJECT_TEMPLATE = 'Coding Boot Camp - Tutorial Confirmation <$date ${starttime}-${endtime}>'
"""
#^^The braces prevent confusion with the hyphen and angle brackets. Use as needed.

TUTOR_EMAIL = #String - email associated with your Gmail account
TUTOR_SENDER = #String - the display name + email address you want in the From header.
"""
Example:

TUTOR_SENDER = '(John Smith) <john.smith@gmail.com>'
"""
#^^THE PARENS ARE NECESSARY FOR SOME DISPLAY NAMES TO SHOW!

EVENT_DESCRIPTION = 'Boot Camp Tutorial Session' #String - Acc. to Tutor Guide, should be 'Boot Camp Tutorial Session', but if different for you, change this

SHEET_NAME = #String - the Sheet ID of the Sheet containing your students' data (see here: https://help.form.io/assets/img/googlesheet/googlesheet-spreadsheet.png)
RANGE_NAME = #String - the Excel-formatted Worksheet name & Range of the data containing the students' names, emails, timezones, and Zoom links (Example: 'Student Roster!C5:G')
NAME_COLUMN = #Int - number specifying the index of the name column in the range specified in RANGE_NAME
EMAIL_COLUMN = 
TZ_COLUMN = 
ZOOM_COLUMN = 
#See guide for variables above here: https://imgur.com/a/q4LClAE

TIMEZONE_STR = #String - UTC Offset of Tutor's timezone in format '+XX:00' or '-XX:00'
"""
Example:

import time

#Check for Daylight Savings Time
is_dst = time.localtime().tm_isdst
TIMEZONE_STR = "-05:00" if is_dst else "-06:00"
"""

TEST_EMAIL = #String - Email address for receiving test emails. Change the value of IS_IN_TEST_MODE to toggle test mode.