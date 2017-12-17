"""A simple rota reader - generates a single icalendar file for the whole rota"""

# _________________________________ IMPORTS _________________________________
from csv import DictReader
from icalendar import Calendar, Event
import uuid
from datetime import datetime, time, timedelta
import pytz

# ________________________________ CONSTANTS ________________________________

# Define our local timezone - this is so that the rota works even when we cross
# into BST/GMT
TZ = pytz.timezone('Europe/London')

# Let's define the hours of work
START_TIME = time(8, tzinfo=TZ)
DURATION = timedelta(hours=12)


# ________________________________ FUNCTIONS ________________________________
def convert_to_date(date_str):
    """Convert a date string into a date with a few fallbacks"""
    try:
        # Let's expect the date to be of the form day / month / 4 digit year
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except ValueError:
        try:
            # OK let's try with 2 digit year?
            return datetime.strptime(date_str, '%d/%m/%y').date()
        except ValueError:
            # OK has it ended up in year first format - if this doesn't work we
            # should fail
            return datetime.strptime(date_str, '%Y/%m/%d').date()


def create_event_for(row):
    """Take a row and create an icalendar event for this row"""
    event = Event()
    event.add('summary', 'On-Call: ' + row['On-Call'])
    event.add('description', 'On-Call: ' + row['On-Call'])
    event.add('dtstart', datetime.combine(convert_to_date(row['Date']),
                                          START_TIME))
    event.add('duration', DURATION)
    event.add('dtstamp', datetime.now())
    event.add('location', 'At work')  # Set this to something useful
    event.add('uid', uuid.uuid4())
    return event


# ___________________________________ MAIN ___________________________________
# Create a basic iCalendar object
cal = Calendar()

# These two lines are required but you can change the prodid slightly
cal.add('prodid', '-//hacksw/handcal/NONSGML v1.0//EN')
cal.add('version', '2.0')

# This means that your calendar gets a nice default name
cal.add('x-wr-calname', 'Simple Rota - Whole Rota')

# Now open the rota
with open('simple_rota.csv') as f:
    reader = DictReader(f)
    for row in reader:
        event = create_event_for(row)
        cal.add_component(event)

with open('simple_rota.ics', 'wb') as f:
    f.write(cal.to_ical())
