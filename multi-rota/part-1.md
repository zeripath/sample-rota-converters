
# Multiple shift - multiple person rotas

[HOME](https://zeripath.github.io/sample-rota-converters)

So we can convert a simple rota like [simple_rota.csv](../simple-rota/simple_rota.csv), but most of our rotas aren't anywhere as simple. Let's do some baby steps, let's consider:

```csv
"Date", "SHO", "SpR", "Consultant"
"29/01/2018", "James", "Martin", "Positano"
"30/01/2018", "James", "Martin", "Positano"
"31/01/2018", "James", "Martin", "Positano"
"01/02/2018", "James", "Martin", "Positano"
"02/02/2018", "Becky", "Peter", "Positano"
"03/02/2018", "Becky", "Peter", "Positano"
"04/02/2018", "Becky", "Peter", "Positano"
"05/02/2018", "Angela", "Jane", "Luko"
```
etc.

Now we want to create rotas for the SHOs, SpRs and the consultants. We'll need their hours.



```python
from datetime import time, timedelta
import pytz

TZ = pytz.timezone('Europe/London')

HOURS = {
    'SHO': {
        'start': time(8, tzinfo=TZ),
        'duration': timedelta(hours=12)
    },
    'SpR': {
        'start': time(8, tzinfo=TZ),
        'duration': timedelta(hours=12)
    },
    'Consultant': {
        'start': time(8, tzinfo=TZ),
        'duration': timedelta(days=1)
    }
}
```

If we look at [simple_rota3.py](../simple-rota/simple_rota3.py) we're going to need to look again at `handle_rows`



```python
def handle_rows(rows, name_to_list_of_rows_dict):
    """Store the rota information by name"""
    for row in rows:
        name = row['On-Call']
        name_to_list_of_rows_dict[ name ].append(row)
        name_to_list_of_rows_dict[ 'All' ].append(row)
```

Now, there are mulitple ways of dealing with this, depending on how the rota co-ordinator works. If it's the case that the same name in the a different column is a different person then we'll need to store the job with the name - we should probably do that in any case - if an SpR acts down or SHO acts up it will probably be marked in some other way. 


```python
def handle_rows(rows, name_to_list_of_rows_dict):
    """Store the rota information by name and job"""
    for row in rows:
        name_to_list_of_rows_dict[ ('All', 'All') ].append(row)
        for key in row:
            if key != 'Date':
                name = row[key]
                name_to_list_of_rows_dict[ (name, key) ].append(row)
```

We'll also have to adjust `create_event_for` and  `create_calendar_for` and pass in the name and job, change the summary and description to include more information, and adjust the hours based on the job.


```python
def create_calendar_for(name, job, rows):
    """Create a calendar for name in job using the provided rows"""
    # Create a basic iCalendar object
    cal = Calendar()

    # These two lines are required but you can change the prodid slightly
    cal.add('prodid', '-//hacksw/handcal/NONSGML v1.0//EN')
    cal.add('version', '2.0')

    # This means that your calendar gets a nice default name
    cal.add('x-wr-calname', 'Simple rota for %s (%s)' % (name, job))
    
    # Now open the rota
    if job == 'All':
        for row in rows:
            for key in row:
                if key != 'Date':
                    event = create_event_for(row[key], key, row)
                    cal.add_component(event)
    else:    
        for row in rows:
            event = create_event_for(name, job, row)
            cal.add_component(event)
        
    return cal

def create_event_for(name, job, row):
    """Create an icalendar event for this row for name and job"""
    event = Event()
    # Description should say who else is in department.
    # Now some calendars will basically need summary the same
    # as description
    description = '{1}: {0} with '.format(name, job)
    others_d = ', '.join([ '{0}: {1}'.format(key, row[key]) \
                          for key in row \
                         if key not in ['Date', job]])
    event.add('description', description + others_d)
    # Change the summary to say the same.
    event.add('summary', description + others_id)
    # This time look up the start time in the HOURS dictionary
    event.add('dtstart', 
              datetime.combine(
                  convert_to_date(row['Date']),
                  HOURS[job]['start']))
    # Similarly look up the duration in the HOURS dictionary
    event.add('duration', HOURS[job]['duration'])
    event.add('dtstamp', datetime.now())
    event.add('location', 'At work') # Set this to something useful
    event.add('uid', uuid.uuid4())
    return event
```

Which of course means we'll have to adjust `check_last_names` and `create_calendars` too


```python
## Check last names functions
def check_last_names(name_to_list_of_rows_dict, directory):
    """Check from the previous run of this parser if there are new names, returns a dictionary of names to number of rows"""
    from os.path import exists, join
    from csv import DictReader, DictWriter
    
    last_names = {}
    # Read the last names 
    if exists(join(directory, 'last_names.csv')):
        with open(join(directory, 'last_names.csv')) as f:
            r = DictReader(f)
            for row in r:
                last_names[(row['name'], row['job'])] = int(row['number'])
    
    name_to_number_of_rows = {}
    with open(join(directory, 'last_names.csv'), 'w') as f:
        w = DictWriter(f, ['name', 'job', 'number'])
        w.writeheader()
        for name, job in name_to_list_of_rows_dict:
            number = len(name_to_list_of_rows_dict[(name, job)])
            if not (name, job) in last_names:
                # We have a new name
                print('New name in rota: %s (%s) with %d rows' % (name, job, number))
            w.writerow( { 'name': name, 'job': job, 'number': number } )
            name_to_number_of_rows[(name, job)] = number
    
    return name_to_number_of_rows

## Writing functions
def create_calendars(name_to_list_of_rows_dict, directory):
    from os.path import join
    for name, job in name_to_list_of_rows_dict:
        rows = name_to_list_of_rows_dict[name]
        cal = create_calendar_for(name, job, rows)
        with open(join(directory, 'rota_%s_%s.ics' % (job, name)), 'wb') as f:
            f.write(cal.to_ical())
```

Now if you make those changes, you'll see that the consultant's shift covers two days, which if you think about it - it does. However, the UI is somewhat unhelpful and it may be better to change the consultant's hours from starting at 8am to midnight.

In any case I've made those changes and they are in the [multi_rota.py](multi_rota.py)

[Back](../)
