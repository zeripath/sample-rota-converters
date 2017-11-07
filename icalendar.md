# The iCalendar format
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

In any case we don't need to hand code these because someone else has done this work for us: The icalendar module https://icalendar.readthedocs.io/en/latest/
