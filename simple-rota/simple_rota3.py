"""A simple rota reader - generates a icalendar files for each person"""

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
START_TIME = time(8, tzinfo=TZ)
DURATION = timedelta(hours=12)

### FUNCTIONS

## Conversion functions 
def convert_to_date(date_str):
    """Convert a date string into a date using dateutil.parser.parse - assume dayfirst notation"""
    return dateutil.parser.parse(date_str, dayfirst=True)

## Calendar functions
def create_event_for(row):
    """Take a row and create an icalendar event for this row"""
    event = Event()
    event.add('summary', 'On-Call: ' + row['On-Call'])
    event.add('description', 'On-Call: ' + row['On-Call'])
    event.add('dtstart', datetime.combine(convert_to_date(row['Date']), START_TIME))
    event.add('duration', DURATION)
    event.add('dtstamp', datetime.now())
    event.add('location', 'At work') # Set this to something useful
    event.add('uid', uuid.uuid4())
    return event

def create_calendar_for(rows, title='Simple Rota'):
    """Create a calendar using the rows"""
    # Create a basic iCalendar object
    cal = Calendar()

    # These two lines are required but you can change the prodid slightly
    cal.add('prodid', '-//hacksw/handcal/NONSGML v1.0//EN')
    cal.add('version', '2.0')

    # This means that your calendar gets a nice default name
    cal.add('x-wr-calname', title)

    # Now open the rota
    for row in rows:
        event = create_event_for(row)
        cal.add_component(event)
        
    return cal

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
    """Given some rows and a data structure to store the rota information in, parse the rows and store the rota information"""
    for row in rows:
        name = row['On-Call']
        name_to_list_of_rows_dict[ name ].append(row)
        name_to_list_of_rows_dict[ 'All' ].append(row)
    

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
                last_names[row['name']] = int(row['number'])
    
    name_to_number_of_rows = {}
    with open(join(directory, 'last_names.csv'), 'w') as f:
        w = DictWriter(f, ['name', 'number'])
        w.writeheader()
        for name in name_to_list_of_rows_dict:
            number = len(name_to_list_of_rows_dict[name])
            if not name in last_names:
                # We have a new name
                print('New name in rota: %s with %d rows' % (name, number))
            w.writerow( { 'name': name, 'number': number } )
            name_to_number_of_rows['name'] = number
    
    return name_to_number_of_rows

## Writing functions
def create_calendars(name_to_list_of_rows_dict, directory):
    from os.path import join
    for name in name_to_list_of_rows_dict:
        rows = name_to_list_of_rows_dict[name]
        cal = create_calendar_for(rows, 'Simple Rota for %s' % name)
        with open(join(directory, 'rota_%s.ics' % name), 'wb') as f:
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
    parser = ArgumentParser(description='Simple Rota reader')
    parser.add_argument('filename', nargs='?', help='the rota filename', default='simple_rota.csv')
    parser.add_argument('directory', nargs='?', help='output directory', default='generated')
    parser.add_argument('--sheet', nargs='?', type=int, help='excel spreadsheet id', default=0)

    args = parser.parse_args()
    
    parse_file_and_create_calendars(args.filename, args.sheet, args.directory)