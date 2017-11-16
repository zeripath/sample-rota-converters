
# Adding night shifts to the multi-shift/multi-person rota

[HOME](https://zeripath.github.io/sample-rota-converters)

Let's consider adding night shifts in to this rota. [multi_rota2.xls](multi_rota2.xls)

```csv
"Date", "SHO", "SpR", "Night SHO", "Night SpR", "Consultant"
"29/01/2018", "James", "Martin", "Tim", "Anusha", "Positano"
"30/01/2018", "James", "Martin", "Tim", "Anusha", "Positano"
"31/01/2018", "James", "Martin", "Tim", "Anusha", "Positano"
"01/02/2018", "James", "Martin", "Tim", "Anusha", "Positano"
"02/02/2018", "Becky", "Peter", "Emma", "Bob", "Positano"
"03/02/2018", "Becky", "Peter", "Emma", "Bob", "Positano"
"04/02/2018", "Becky", "Peter", "Emma", "Bob", "Positano"
"05/02/2018", "Angela", "Jane", "Jenny", "Martin", "Smith"
```
etc.

We'll need to adjust the `HOURS` dictionary:


```python
from datetime import time, timedelta
import pytz

TZ = pytz.timezone('Europe/London')

HOURS = {
    'SHO': {
        'start': time(8, tzinfo=TZ),
        'duration': timedelta(hours=12.5)
    },
    'SpR': {
        'start': time(8, tzinfo=TZ),
        'duration': timedelta(hours=12.5)
    },
    'Consultant': {
        'start': time(8, tzinfo=TZ),
        'duration': timedelta(days=1)
    },
    'Night SHO': {
        'start': time(20, tzinfo=TZ),
        'duration': timedelta(hours=12.5)        
    },
    'Night SpR': {
        'start': time(20, tzinfo=TZ),
        'duration': timedelta(hours=12.5)                
    }
}
```

There's a problem with this though: Daylight Savings Time.

## Daylight Savings Time: Duration vs End Time

Shifts tend to finish at the same time every day - therefore we should switch from using `duration` to `end`. (But we'll have to be careful to check if the end time is earlier than the start time, and shift the day if necessary.)


```python
HOURS = {
    'SHO': {
        'start': time(8, tzinfo=TZ),
        'end': time(20, 30, tzinfo=TZ)
    },
    'SpR': {
        'start': time(8, tzinfo=TZ),
        'end': time(20, 30, tzinfo=TZ)
    },
    'Consultant': {        
        'duration': timedelta(days=1)
    },
    'Night SHO': {
        'start': time(20, tzinfo=TZ),
        'end': time(8, 30, tzinfo=TZ)
    },
    'Night SpR': {
        'start': time(20, tzinfo=TZ),
        'end': time(8, 30, tzinfo=TZ)
    }

}
```


```python
def create_event_for(name, job, row):
    """Create an icalendar event for this row for name and job"""
    event = Event()
    
    # Description should say who else is in department.
    description = '{1}: {0} with '.format(name, job)
    others_d = ', '.join([ '{1}: {0}'.format(key, row[key]) \
                          for key in row \
                         if key not in ['Date', job]])
    event.add('description', description + others_d)
    
    # Make the summary the same as the description
    event.add('summary', description + others_d)
    
    if 'start' in HOURS[job]:
        # If we have a start time in the HOURS dictionary for this job - combine it with date
        event.add('dtstart', 
                  datetime.combine(
                      convert_to_date(row['Date']),
                      HOURS[job]['start']))
    else:
        # Otherwise just use the date
        event.add('dtstart', convert_to_date(row['Date']).date())

    if 'duration' in HOURS[job]:
        event.add('duration', HOURS[job]['duration'])
    else:
        if (HOURS[job]['end'] > HOURS[job]['start']):
            event.add('dtend',
                      datetime.combine(
                          convert_to_date(row['Date']),
                          HOURS[job]['end']))            
        else:
            # OK so the end is before the start?
            # simply add a day on to the date and then combine
            event.add('dtend',
                      datetime.combine(
                          convert_to_date(row['Date']) + timedelta(days=1),
                          HOURS[job]['end']))

    event.add('dtstamp', datetime.now())
    event.add('location', 'At work') # Set this to something useful
    event.add('uid', uuid.uuid4())
    return event
```

## Job versus Role
If you make the above changes you'll notice a problem, you'll get separate rotas for night SHO and day SHO. The problem is that we've made the role synonymous with the job i.e. `Night SHO` is a role in the job `SHO`.

So we need to tell the rota to merge the `Night SHO` and the `SHO` roles together into an `SHO` job. Let's start by adjusting the `HOURS` dictionary to add a job descriptor to these, and we'll let the default job of the others be their name.


```python
HOURS = {
    'SHO': {
        'start': time(8, tzinfo=TZ),
        'end': time(20, 30, tzinfo=TZ)
    },
    'SpR': {
        'start': time(8, tzinfo=TZ),
        'end': time(20, 30, tzinfo=TZ)
    },
    'Consultant': {        
        'duration': timedelta(days=1)
    },
    'Night SHO': {
        'job': 'SHO',
        'start': time(20, tzinfo=TZ),
        'end': time(8, 30, tzinfo=TZ)
    },
    'Night SpR': {
        'job': 'SpR',
        'start': time(20, tzinfo=TZ),
        'end': time(8, 30, tzinfo=TZ)
    }

}
```

Unfortunately, in order to account for this we're going to have to change a lot of things.

Let's think about our primary data-structure `names_to_list_of_rows_dict`. 

We've already adjusted this to actually be a dictionary of `(name, job)` pairs to a list of `rows` (or less wordily `(name, job) → list(row)`). The simplest thing change that this data-structure can undergo is a change to a dictionary: `(name, job) → list(role, list(row))` (i.e. a dictionary of `(name, job)` pairs to a list of `(role, rows)` pairs. Note `rows` here is a list.)

So let's look at `handle_rows(...)`


```python
# multi_rota.py and simple_rota3.py
def handle_rows(rows):
    """Store the rota information by name and job"""
    name_to_list_of_rows_dict = defaultdict(list)
    for row in rows:
        name_to_list_of_rows_dict[ ('All', 'All') ].append(row)
        for key in row:
            if key != 'Date':
                name = row[key]
                name_to_list_of_rows_dict[ (name, key) ].append(row)
    return name_to_list_of_rows_dict
```

As mentioned above `name_to_list_of_rows_dict` is poorly named and should be `name_job_to_list_of_rows_dict` - or using our new notation `name_role_to_list_of_rows_dict` (which is a bit of a mouthful!) and has type `(name, role) → list(rows)`.

If we iterate across that dictionary, mapping the `role` to its `job` and create a new dictionary with type: `(name, job) → list(role, list(row))` which for brevity I'll call `nj_to_rrows` then we can use that as our primary data structure.


```python
# multi_rota2.py
def handle_rows(rows):
    """Store the rota information by name and job"""
    # nr_to_rows: name_role_to_list_of_rows_dict
    nr_to_rows = defaultdict(list)
    for row in rows:
        nr_to_rows[ ('All', 'All') ].append(row)
        for key in row:
            if key != 'Date':
                name = row[key]
                nr_to_rows[ (name, key) ].append(row)

    # nj_to_rrows: name_job_to_list_role_rows_dict 
    nj_to_rrows = defaultdict(list)

    for name, role in nr_to_rows:
        job = HOURS[role]['job'] \
            if role in HOURS and 'job' in HOURS[role] \
            else role
        rows = nr_to_rows[ (name, role) ]
        
        nj_to_rrows[ (name, job) ].append( (role, rows) )

    return nj_to_rrows
```

* _Now we could do that in one pass but, it's a bit complicated and I think it's easier to read like this._

We should probably adjust `parse_file_and_create_calendars(...)` if only to just to change the name of the data-structure - but also to remind us what needs changing.


```python
## Main function
def parse_file_and_create_calendars(fname, sheet, directory):
    from os.path import exists
    rows_data = read(fname, handle_rows, sheet)
    
    if not exists(directory):
        from os import makedirs
        makedirs(directory)
    check_last_names(rows_data, directory)
    create_calendars(rows_data, directory)

```

## Adjusting `check_last_names`

Now if we recall `check_last_names(...)` it prints out a list of new names with the number of rows that are affected. We'll need to therefore adjust this too


```python
## Check last names functions
def check_last_names(nj_to_r_rows, directory):
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
        for name, job in nj_to_r_rows:
            # number is the sum of rows for each role for this name, job pair 
            number = sum( (len(rows) \
                           for _, rows in \
                               nj_to_r_rows[ (name, job) ]))
            if not (name, job) in last_names:
                # We have a new name
                print('New name in rota: %s (%s) with %d rows' % (name, job, number))
            w.writerow( { 'name': name, 'job': job, 'number': number } )
            name_to_number_of_rows[(name, job)] = number
    
    return name_to_number_of_rows
```

## Adjusting `create_calendars`

Next we need to look at `create_calendars`


```python
## multi_rota.py and simple_rota3.py
def create_calendars(name_to_list_of_rows_dict, directory):
    from os.path import join
    for name, job in name_to_list_of_rows_dict:
        rows = name_to_list_of_rows_dict[(name, job)]
        cal = create_calendar_for(name, job, rows)
        with open(join(directory, 'rota_%s_%s.ics' % (job, name)), 'wb') as f:
            f.write(cal.to_ical())
```

Surprisingly, if we simply change `create_calendar_for` to do the right thing this code doesn't need changing. I'll adjust the names for clarity however.


```python
## Writing functions
def create_calendars(nj_to_r_rows, directory):
    from os.path import join
    for name, job in nj_to_r_rows:
        role_rows_pairs = nj_to_r_rows[(name, job)]
        cal = create_calendar_for(name, job, role_rows_pairs)
        with open(join(directory, 'rota_%s_%s.ics' % (job, name)), 'wb') as f:
            f.write(cal.to_ical())
```

## Down the rabbit hole: `create_calendar_for`

So we look at `create_calendar_for`:


```python
## multi_rota.py and simple_rota3.py
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
```

Now instead of passing in a list of `rows` we're passing in a list of `(role, rows)` pairs, so we'll need to iterate across each pair and then the rows, but assuming we do that, how do we need to change `create_event_for`?


```python
# multi_rota.py
def create_event_for(name, job, row):
    """Create an icalendar event for this row for name and job"""
    event = Event()
    
    # Description should say who else is in department.
    description = '{0}: {1} with '.format(job, name)
    others_d = ', '.join([ '{0}: {1}'.format(key, row[key]) \
                          for key in row \
                         if key not in ['Date', job]])
    event.add('description', description + others_d)
    
    # Make the summary the same as the description
    event.add('summary', description + others_d)
    
    if 'start' in HOURS[job]:
        # If we have a start time in the HOURS dictionary for this job - combine it with date
        event.add('dtstart', 
                  datetime.combine(
                      convert_to_date(row['Date']),
                      HOURS[job]['start']))
    else:
        # Otherwise just use the date
        event.add('dtstart', convert_to_date(row['Date']).date())

    if 'duration' in HOURS[job]:
        event.add('duration', HOURS[job]['duration'])
    else:
        if (HOURS[job]['end'] > HOURS[job]['start']):
            event.add('dtend',
                      datetime.combine(
                          convert_to_date(row['Date']),
                          HOURS[job]['end']))            
        else:
            # OK so the end is before the start?
            # simply add a day on to the date and then combine
            event.add('dtend',
                      datetime.combine(
                          convert_to_date(row['Date']) + timedelta(days=1),
                          HOURS[job]['end']))

    event.add('dtstamp', datetime.now())
    event.add('location', 'At work') # Set this to something useful
    event.add('uid', uuid.uuid4())
    return event
```

Looking at this carefully, If we simply replace `job` with `role` here we don't need to change anything! (I'll leave that as a simple task for you!)

Thus we can change our `create_calendar_for` to pass in the `role` instead of the `job` we'll get a working rota!


```python
def create_calendar_for(name, job, role_rows_list):
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
        for _, rows in role_rows_list:
            for row in rows:
                for key in row:
                    if key != 'Date':
                        event = create_event_for(row[key], key, row)
                        cal.add_component(event)
    else:
        for role, rows in role_rows_list:
            for row in rows:
                event = create_event_for(name, role, row)
                cal.add_component(event)
        
    return cal
```

Excellent we now have a working rota reader for night shifts! [multi_rota2.py](multi_rota2.py)

* _Note the amount of work we had to do fix the broken assumption that jobs were equivalent to roles vs. the broken assumption that shifts had a simple start time and duration._
* _In the second case all we had to do was a one for one switch of end time for duration, whereas the first case introduced a new layer of indirection_

[Back](../)