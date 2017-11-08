# A simple rota

[HOME](https://zeripath.github.io/sample-rota-converters)

OK, so we now know what we want to convert our rota into and have a basic idea of how to go about making an icalendar. So let's look at a simple csv rota.

```csv
"Date","On-Call"
"01/01/2018","James"
"02/01/2018","Rebecca"
"03/01/2018","William"
"04/01/2018","James"
"05/01/2018","Rebecca"
"06/01/2018","William"
...
```

I don't believe anyone has ever been given a rota as simple as this. But let's look at it.

## Is it really that simple?

Although this looks like a really simple rota, there's a quite a bit of missing information and context here:

1. What are the hours that the on-call doctor works?
2. Are we sure that we can trust the format of the date to never change?
3. Is it always the case that the On-Call column is always just a single name - the forename of the doctor?

Right, so let's assume that the on-call hours are same everyday, say 8am to 8pm, that the date format is always `DD/MM/YYYY` and that yes it is only a forename of the doctor.

## How do you solve a problem like the simple rota?

What are our inputs? Easy, it's `simple_rota.csv`. We could pass in a name too, or maybe output filename but let's start simple.

What's our output? We want an iCalendar file. But an iCalendar file of what? Let's start by converting the `simple_rota.csv` to a single calendar for the whole rota. (We probably want to output separate files for each participant in future.)

Let's break it down

1. Create an icalendar
2. Read the csv in
3. For each row in the csv: We need to create an event for each day and add the event to icalendar
4. Finally save the icalendar file at the end.

One of these steps hides a lot of work...

### 1. Create an icalendar
We can use the similar code to that in our [introduction to the icalendar format](../icalendar) to create the calendar.

### 2. Read the CSV in
We can just use `DictReader` for this.

### 3. Create events for each day
Ah this is the interesting question!

Let's recall the event code from the [introduction to icalendar](../icalendar):

```python
# Create a lecture event
event = Event()
event.add('summary', 'Give a lecture on iCalendar')
event.add('description', 'Teach people how to create iCalendar from rotas')
event.add('dtstart', datetime(2018, 3, 28, 9, 45, 0, tzinfo=TZ))
event.add('duration', timedelta(minutes=60))
event.add('dtstamp', datetime.now())
event.add('location', 'Here')
event.add('uid', uuid.uuid4())
```

We need 4 things:

1. Summary and Description.
2. A start date and time for the event
3. A duration for the event.
4. A location for the event.

Now the summary and description for these events should probably be the same thing: The name of doctor on-call perhaps prefixed by `"On-Call: "`

The start date will be the date in the first column - but that is just a string and we want a `datetime` or a `date` and `time` that can be combined using `datetime.combine(date, time)` to a `datetime`.

We could split the date string by the `/` character and turn each component into a number:


```python
from datetime import datetime

def convert_to_date(date_str):
    parts = date_str.split('/')
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])
    return datetime(year, month, day).date()

date_str = '01/01/2018'
print(convert_to_date(date_str).isoformat())
```

    2018-01-01


but there's a better way to do this and one that allows us to cope with malformed dates - `datetime.strptime(...)`.

`datetime.strptime` is a function which takes a date in string form and format string like `%d/%m/%Y` and creates a `datetime` that matches it. If there is an error it will raise a `ValueError` and you can try a different format.


```python
def convert_to_date(date_str):
    try:
        # Let's expect the date to be of the form day / month / 4 digit year
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except ValueError:
        try:
            # OK let's try with 2 digit year?
            return datetime.strptime(date_str, '%d/%m/%y').date()
        except ValueError:
            # OK has it ended up in year first format - if this doesn't work we should fail
            return datetime.strptime(date_str, '%Y/%m/%d').date()

print(convert_to_date(date_str).isoformat())
```

    2018-01-01


As clever as this is - it won't cope with dates that haven't got `/` as the separator. I'll leave the solution as an exercise for the moment...

So we've got a start date and the start time is by definition `time(hour=8, tzinfo=TZ)`. So we can set the dtstart value like this.

`event.add('dtstart', datetime.combine(convert_to_date(row['Date']), time(hour=8, tzinfo=TZ)))`



```python
from datetime import date, time, datetime, timedelta

def create_event_for(row):
    event = Event()
    event.add('summary', 'On-Call: ' + row['On-Call'])
    event.add('description', 'On-Call: ' + row['On-Call'])
    event.add('dtstart', datetime.combine(convert_to_date(row['Date']), time(hour=8, tzinfo=TZ)))
    event.add('duration', timedelta(hours=12))
    event.add('dtstamp', datetime.now())
    event.add('location', 'At work') # Set this to something useful
    event.add('uid', uuid.uuid4())
    return event

print(str(create_event_for({'Date': '01/01/2018', 'On-Call': 'James'}).to_ical(), 'utf-8'))
```

    BEGIN:VEVENT
    SUMMARY:On-Call: James
    DTSTART;TZID=Europe/London;VALUE=DATE-TIME:20180101T080000
    DURATION:PT12H
    DTSTAMP;VALUE=DATE-TIME:20171105T210255Z
    UID:7c5d9b0d-4915-4d75-8493-da559e69112e
    DESCRIPTION:On-Call: James
    LOCATION:At work
    END:VEVENT



### 4. Write an iCalendar file at the end
Save the calendar text with:
```python
with open(output_filename, 'wb') as f:
    f.write(cal.to_ical())
```

So now we've got all the components necessary to build a simple rota reader and I've put them all together in [simple_rota1.py](simple_rota1.py)

[Back](../)
