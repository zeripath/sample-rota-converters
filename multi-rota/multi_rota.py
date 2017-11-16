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
        'duration': timedelta(hours=12)
    },
    'SpR': {
        'start': time(8, tzinfo=TZ),
        'duration': timedelta(hours=12)
    },
    'Consultant': {        
        'duration': timedelta(days=1)
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

    # Look up the duration in the HOURS dictionary
    event.add('duration', HOURS[job]['duration'])

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
        handler(r, *args, **kwds)

def read_excel(fname, handler, sheet=0, *args, **kwds):
    """Reads the given excel file *fname* as DictReader and calls handler with the first argument as the reader. Optional and named parameters are passed to the provided handler"""
    from xlrd_helper import DictReader
    with open(fname, 'rb') as f:
        r = DictReader(f, sheet_index=sheet)
        handler(r, *args, **kwds)
            
def read(fname, handler, sheet=0, *args, **kwds):    
    """Attempt to read given file *fname* as a DictReader and calls handler with the first argument as the reader. Optional and named parameters are passed to the provided handler"""
    if fname.lower().endswith('.csv'):
        read_csv(fname, handler, sheet, *args, **kwds) 
    elif fname.lower().endswith('.xls') or fname.lower().endswith('.xlsx'):
        read_excel(fname, handler, sheet, *args, **kwds)
    else:
        raise ValueError('Unknown filetype: %s' % fname)

## Reading functions
def handle_rows(rows, name_to_list_of_rows_dict):
    """Store the rota information by name and job"""
    for row in rows:
        name_to_list_of_rows_dict[ ('All', 'All') ].append(row)
        for key in row:
            if key != 'Date':
                name = row[key]
                name_to_list_of_rows_dict[ (name, key) ].append(row)
    

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
        rows = name_to_list_of_rows_dict[(name, job)]
        cal = create_calendar_for(name, job, rows)
        with open(join(directory, 'rota_%s_%s.ics' % (job, name)), 'wb') as f:
            f.write(cal.to_ical())

## Main function
def parse_file_and_create_calendars(fname, sheet, directory):
    from os.path import exists
    name_to_list_of_rows_dict = defaultdict(list)
    read(fname, handle_rows, sheet, name_to_list_of_rows_dict)
    
    if not exists(directory):
        from os import makedirs
        makedirs(directory)
    check_last_names(name_to_list_of_rows_dict, directory)
    create_calendars(name_to_list_of_rows_dict, directory)

### MAIN
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Multi Rota reader')
    parser.add_argument('filename', nargs='?', help='the rota filename', default='multi_rota.xls')
    parser.add_argument('directory', nargs='?', help='output directory', default='generated')
    parser.add_argument('--sheet', nargs='?', type=int, help='excel spreadsheet id', default=0)

    args = parser.parse_args()
    
    parse_file_and_create_calendars(args.filename, args.sheet, args.directory)