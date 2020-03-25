## Trilogy Tutor Auto-Confirmation Emailer

###by Earnest Long, Jr., Senior Data Visualization Tutor

**Description:**

A simple script that automates sending confirmation emails to students that have tutoring sessions scheduled for the next day.

The script uses the Gmail, Google Calendar, and Google Sheets APIs to 1) extract the events, 2) identify each student's email and timezone, 3) construct emails with the appropriate names, dates, and times, and 4) send the emails.

**Requirements:**

* Gmail, Google Calendar, and Google Sheets accounts holding all the relevant data **all associated with the same Google Account**.

**Installation:**

1. Clone the repository and pip install the requirements.

2. Enable the Gmail, Google Calendar, and Google Sheets APIs in your Google account.
 * The Easy Way:
    * Follow Step 1 of each of the guides here (don't download credentials.json until the 3rd link, when all APIs are enabled):
        * Gmail: https://developers.google.com/gmail/api/quickstart/python
        * Calendar: https://developers.google.com/calendar/quickstart/python
        * Sheets: https://developers.google.com/sheets/api/quickstart/python
    * After enabling all 3 APIs, download the credentials.json file into the project directory.
 * The Hard(er) Way:
    * Create a project in the Google Developer Console, enable the APIs for that project, manually create the credentials file, then download to the project directory.

3. Create the following:

 1. A file named **config.py** declaring the variables shown in config_example.py.
 2. A file named **msg_template.html** that contains the HTML email message with customizable Template variables (docs here: https://docs.python.org/2.4/lib/node109.html) as seen in msg\_template\_example.html.

**Notes:**

* The script uses the Calendar event description to distinguish Trilogy tutoring sessions from other Calendar events. Calendly auto-populates the description field of new events, but if you manually create an event for a student, the script won't detect it if you don't supply the expected description!

* Sometimes students sign up for sessions on Calendly with a different email than what's given in the Tutor Assignment Email. If the script can't find the email address on the event in the Sheets email column, it will prompt you for the correct address or to enter 'skip' to skip that event.

* As it stands, the script expects the timezones in the Sheets worksheet to contain the appropriate US timezone abbreviation in all caps. Modify the code to suit the format you use in your Sheet (~line 182).

* If one of the fields for a student whose session is tomorrow is blank (e.g. the Zoom link), the script will throw an error. It expects to find a name, email, timezone, and Zoom link for each scheduled student.

* Please feel free to branch and improve!

* And if you run into any issues, Slack me or use the issues tab.

**Thanks!**