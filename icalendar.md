# The iCalendar format

[HOME](https://zeripath.github.io/sample-rota-converters)

## What does an iCalendar file look like?

```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal/NONSGML v1.0//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Basic Example
X-WR-TIMEZONE:Europe/London
BEGIN:VTIMEZONE
TZID:Europe/London
X-LIC-LOCATION:Europe/London
BEGIN:DAYLIGHT
TZOFFSETFROM:+0000
TZOFFSETTO:+0100
TZNAME:BST
DTSTART:19700329T010000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0100
TZOFFSETTO:+0000
TZNAME:GMT
DTSTART:19701025T020000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
DTSTAMP:201803027T200000Z
DTSTART;TZID=Europe/London:20180328T094500
DURATION:PT60M
ORGANIZER:MAILTO:art27@cantab.net
LOCATION:Here
SUMMARY:Give an lecture on iCalendar
UID:UID20180328T094500PT60M
END:VEVENT
END:VCALENDAR
```

Ugh! What a horror! But if you look carefully there's a block structure:

```ics
BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//hacksw/handcal/NONSGML v1.0//EN
    CALSCALE:GREGORIAN
    METHOD:PUBLISH
    X-WR-CALNAME:Basic Example
    X-WR-TIMEZONE:Europe/London

    BEGIN:VTIMEZONE
        TZID:Europe/London
        X-LIC-LOCATION:Europe/London

        BEGIN:DAYLIGHT
            TZOFFSETFROM:+0000
            TZOFFSETTO:+0100
            TZNAME:BST
            DTSTART:19700329T010000
            RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
        END:DAYLIGHT

        BEGIN:STANDARD
            TZOFFSETFROM:+0100
            TZOFFSETTO:+0000
            TZNAME:GMT
            DTSTART:19701025T020000
            RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
        END:STANDARD
    END:VTIMEZONE

    BEGIN:VEVENT
        DTSTAMP:201803027T200000Z
        DTSTART;TZID=Europe/London:20180328T094500
        DURATION:PT60M
        ORGANIZER:MAILTO:art27@cantab.net
        LOCATION:Here
        SUMMARY:Give an lecture on iCalendar
        UID:UID20180328T094500PT60M
    END:VEVENT
END:VCALENDAR
```

Now there are number of gotchas with this format, and most calendar applications will just ignore your calendar if you get the format slightly wrong. So, although it looks simple you should probably not just hand code these yourselves.

* Here's an example: The maximum length of a line 72 characters - but you can represent lines longer than this by indenting on the next line.

In any case we don't need to hand code these because someone else has done this work for us: The icalendar module [https://icalendar.readthedocs.io/en/latest/]

```python
# OK let's ensure that you have the necessary software
try:
    import icalendar
except ModuleNotFoundError:
    !pip install --user icalendar

try:
    import pytz
except ModuleNotFoundError:
    !pip install --user pytz

try:
    import datetime
except ModuleNotFoundError:
    !pip install --user datetime

try:
    import uuid
except ModuleNotFoundError:
    !pip install --user uuid

# Now let's grab some modules
from icalendar import Calendar, Event
import pytz
from datetime import datetime, timedelta

# Define our timezone - have a think why this is necessary!
TZ = pytz.timezone('Europe/London')

# Create a basic iCalendar object
cal = Calendar()

# These two lines are required but you can change the prodid slightly
cal.add('prodid', '-//hacksw/handcal/NONSGML v1.0//EN')
cal.add('version', '2.0')

# This means that your calendar gets a nice default name
cal.add('x-wr-calname', 'Basic Example')

# Now let's make an event
event = Event()
event.add('summary', 'Give a lecture on iCalendar')
event.add('description', 'Teach people how to create iCalendar from rotas')
event.add('dtstart', datetime(2018, 3, 28, 9, 45, 0, tzinfo=TZ))
event.add('duration', timedelta(minutes=60))
event.add('dtstamp', datetime.now())
event.add('location', 'Here')
event.add('uid', uuid.uuid4())

# Add the event
cal.add_component(event)

# Finally show what the calendar looks like
print (str(cal.to_ical(), 'utf8'))
```

    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//hacksw/handcal/NONSGML v1.0//EN
    X-WR-CALNAME:Basic Example
    BEGIN:VEVENT
    SUMMARY:Give a lecture on iCalendar
    DTSTART;TZID=Europe/London;VALUE=DATE-TIME:20180328T094500
    DURATION:PT1H
    DTSTAMP;VALUE=DATE-TIME:20171105T212901Z
    UID:296d0a24-2fac-4e62-982e-103d27409630
    DESCRIPTION:Teach people how to create iCalendar from rotas
    LOCATION:Here
    END:VEVENT
    END:VCALENDAR
    


w00t! We can make an iCalendar file! 

_If you look at the result of that calendar, it looks different from the handcoded one. Does it matter? It probably doesn't - but it shows a problem with the format - there are multiple ways of doing the same thing!_

[Back](/)
