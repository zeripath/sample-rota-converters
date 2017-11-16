"""A rota reader for the multi_rota - generates a icalendar files for each person"""

### IMPORTS

from icalendar import Calendar, Event
import uuid
from datetime import date, datetime, time, timedelta
from collections import defaultdict
import pytz
import dateutil.parser

### CONSTANTS

# Define our local timezone - this is so that the rota works even when we cross into BST/GMT
TZ = pytz.timezone('Europe/London')

# Let's define the hours of work
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

### FUNCTIONS

## Conversion functions 
def convert_to_date(date_str):
    """Convert a date string into a date using dateutil.parser.parse - assume dayfirst notation"""
    try:
        return datetime.strptime(date_str, '%Y/%m/%d')
    except ValueError:
        return dateutil.parser.parse(date_str, dayfirst=True)

## Calendar functions
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

def create_event_for(name, role, row):
    """Create an icalendar event for this row for name and role"""
    event = Event()
    
    # Description should say who else is in department.
    description = '{0}: {1} with '.format(role, name)
    others_d = ', '.join([ '{0}: {1}'.format(key, row[key]) \
                          for key in row \
                         if key not in ['Date', role]])
    event.add('description', description + others_d)
    
    # Make the summary the same as the description
    event.add('summary', description + others_d)
    
    if 'start' in HOURS[role]:
        # If we have a start time in the HOURS dictionary for this role
        # - combine it with date
        event.add('dtstart', 
                  datetime.combine(
                      convert_to_date(row['Date']),
                      HOURS[role]['start']))
    else:
        # Otherwise just use the date
        event.add('dtstart', convert_to_date(row['Date']).date())

    if 'duration' in HOURS[role]:
        event.add('duration', HOURS[role]['duration'])
    else:
        if (HOURS[role]['end'] > HOURS[role]['start']):
            event.add('dtend',
                      datetime.combine(
                          convert_to_date(row['Date']),
                          HOURS[role]['end']))            
        else:
            # OK so the end is before the start?
            # simply add a day on to the date and then combine
            event.add('dtend',
                      datetime.combine(
                          convert_to_date(row['Date']) + timedelta(days=1),
                          HOURS[role]['end']))

    event.add('dtstamp', datetime.now())
    event.add('location', 'At work') # Set this to something useful
    event.add('uid', uuid.uuid4())
    return event

## File reading functions
def read_csv(fname, handler, sheet, *args, **kwds):
    """Reads the given csv file *fname* as DictReader and calls handler with the first argument as the reader. Optional and named parameters are passed to the provided handler"""
    from csv import DictReader
    with open(fname) as f:
        r = DictReader(f)
        return handler(r, *args, **kwds)

def read_excel(fname, handler, sheet=0, *args, **kwds):
    """Reads the given excel file *fname* as DictReader and calls handler with the first argument as the reader. Optional and named parameters are passed to the provided handler"""
    from xlrd_helper import DictReader
    with open(fname, 'rb') as f:
        r = DictReader(f, sheet_index=sheet)
        return handler(r, *args, **kwds)
            
def read(fname, handler, sheet=0, *args, **kwds):    
    """Attempt to read given file *fname* as a DictReader and calls handler with the first argument as the reader. Optional and named parameters are passed to the provided handler"""
    if fname.lower().endswith('.csv'):
        return read_csv(fname, handler, sheet, *args, **kwds) 
    elif fname.lower().endswith('.xls') or fname.lower().endswith('.xlsx'):
        return read_excel(fname, handler, sheet, *args, **kwds)
    else:
        raise ValueError('Unknown filetype: %s' % fname)

## Reading functions
def handle_rows(rows):
    """Store the rota information by name and job"""
    # nr_to_rows: name_to_list_of_rows_dict
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
            if role in HOURS and 'job' in HOURS[role] else role
        rows = nr_to_rows[ (name, role) ]
        
        nj_to_rrows[ (name, job) ].append( (role, rows) )

    return nj_to_rrows
    

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

## Writing functions
def create_calendars(nj_to_r_rows, directory):
    from os.path import join
    for name, job in nj_to_r_rows:
        role_rows_pairs = nj_to_r_rows[(name, job)]
        cal = create_calendar_for(name, job, role_rows_pairs)
        with open(join(directory, 'rota_%s_%s.ics' % (job, name)), 'wb') as f:
            f.write(cal.to_ical())

## Main function
def parse_file_and_create_calendars(fname, sheet, directory):
    from os.path import exists
    rows_data = read(fname, handle_rows, sheet)
    
    if not exists(directory):
        from os import makedirs
        makedirs(directory)
    check_last_names(rows_data, directory)
    create_calendars(rows_data, directory)

### MAIN
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Multi Rota reader')
    parser.add_argument('filename', nargs='?', help='the rota filename', default='multi_rota2.xls')
    parser.add_argument('directory', nargs='?', help='output directory', default='generated')
    parser.add_argument('--sheet', nargs='?', type=int, help='excel spreadsheet id', default=0)

    args = parser.parse_args()
    
    parse_file_and_create_calendars(args.filename, args.sheet, args.directory)