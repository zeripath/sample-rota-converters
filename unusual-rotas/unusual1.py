#!/usr/bin/python3
"""A rota reader for the unusual1 rota - generates a icalendar files for each
person"""

# __________________________________ IMPORTS __________________________________
from icalendar import Calendar, Event
import uuid
from datetime import date, datetime, timedelta
from collections import defaultdict
import pytz
import dateutil.parser

# _________________________________ CONSTANTS _________________________________
# Define our local timezone
# - this is so that the rota works even when we cross into BST/GMT
TZ = pytz.timezone('Europe/London')

# Let's define the hours of work
HOURS = {
    'On-Call': {
        'duration': timedelta(days=1)
    },
    'Lieu': {
        'duration': timedelta(days=1)
    }
}

BETWEEN = (date(2017, 12, 6), date(2018, 3, 7))

START_DAY = date(2016, 1, 1)

# _________________________________ FUNCTIONS _________________________________
# Spelling corrections
SPELLING_CORRECTIONS = {}
UNNECESSARY_ADDITIONAL_INFORMATION_RES = []


def strip_unnecessary_information(name):
    canonical = name.upper().strip()
    for reg_exp in UNNECESSARY_ADDITIONAL_INFORMATION_RES:
        if reg_exp.match(canonical):
            canonical = reg_exp.match(canonical).groups()[0]
    return canonical


def autocorrect(name):
    canonical = strip_unnecessary_information(name)
    if canonical in SPELLING_CORRECTIONS:
        return SPELLING_CORRECTIONS[canonical].upper().strip()
    return canonical.upper()


# Calendar functions
def create_calendar_for(name, dates, between):
    """Create a calendar for name in job using the provided rows"""
    # Create a basic iCalendar object
    cal = Calendar()

    # These two lines are required but you can change the prodid slightly
    cal.add('prodid', '-//hacksw/handcal/NONSGML v1.0//EN')
    cal.add('version', '2.0')

    # This means that your calendar gets a nice default name
    cal.add('x-wr-calname', 'Unusual-1 on-call rota for %s' % (name))

    # Now open the rota
    if name == 'All':
        for day, name, additional in dates:
            if (day >= between[0] and day < between[1]):
                if day.weekday() == 5:  # SAT
                    # Get a day off before
                    cal.add_component(
                        create_event_for('Lieu',
                                         day - timedelta(days=1),
                                         '',
                                         name))
                cal.add_component(create_event_for('On-Call',
                                                   day,
                                                   additional,
                                                   name))
                if day.weekday() < 4 or day.weekday() == 6:  # MON-THURS or SUN
                    # Get a day off afterwards
                    cal.add_component(
                        create_event_for('Lieu',
                                         day + timedelta(days=1),
                                         '',
                                         name))
    else:
        for day, name, additional in dates:
            # OK first of all create the on-call event for this day
            if (day >= between[0] and day < between[1]):
                if day.weekday() == 5:  # SAT
                    # Get a day off before
                    cal.add_component(
                        create_event_for('Lieu', day - timedelta(days=1)))
                cal.add_component(create_event_for('On-Call', day, additional))
                if day.weekday() < 4 or day.weekday() == 6:  # MON-THURS or SUN
                    # Get a day off afterwards
                    cal.add_component(
                        create_event_for('Lieu', day + timedelta(days=1)))
    return cal


def create_event_for(role, day, additional='', name=''):
    """Create an icalendar event for this row for name and role"""
    event = Event()

    # Munge the role

    # Description should say who else is in department.
    description = role + \
        (': %s' % name if name != '' else '') + \
        (' (%s)' % additional if additional != '' else '')
    event.add('description', description)

    # Make the summary the same as the description
    event.add('summary', description)

    if 'start' in HOURS[role]:
        # If we have a start time in the HOURS dictionary for this role
        # - combine it with date
        event.add('dtstart',
                  datetime.combine(
                      day,
                      HOURS[role]['start']))
    else:
        # Otherwise just use the date
        event.add('dtstart', day)

    if 'duration' in HOURS[role]:
        event.add('duration', HOURS[role]['duration'])
    else:
        if (HOURS[role]['end'] > HOURS[role]['start']):
            event.add('dtend',
                      datetime.combine(
                          day,
                          HOURS[role]['end']))
        else:
            # OK so the end is before the start?
            # simply add a day on to the date and then combine
            event.add('dtend',
                      datetime.combine(
                          day + timedelta(days=1),
                          HOURS[role]['end']))

    event.add('dtstamp', datetime.now())
    event.add('location', 'At work')  # Set this to something useful
    event.add('uid', uuid.uuid4())
    return event


# File reading functions
def read_csv(fname, handler, sheet, *args, **kwds):
    """Reads the given csv file *fname* as DictReader and calls handler with
    the first argument as the reader. Optional and named parameters are passed
    to the provided handler"""
    from csv import Reader
    with open(fname) as f:
        r = Reader(f)
        return handler(r, *args, **kwds)


def read_excel(fname, handler, sheet=0, *args, **kwds):
    """Reads the given excel file *fname* as DictReader and calls handler with
    the first argument as the reader. Optional and named parameters are passed
    to the provided handler"""
    from xlrd_helper import Reader
    with open(fname, 'rb') as f:
        r = Reader(f, sheet_index=sheet)
        return handler(r, *args, **kwds)


def read(fname, handler, sheet=0, *args, **kwds):
    """Attempt to read given file *fname* as a DictReader and calls handler
    with the first argument as the reader. Optional and named parameters are
    passed to the provided handler"""
    if fname.lower().endswith('.csv'):
        return read_csv(fname, handler, sheet, *args, **kwds)
    elif fname.lower().endswith('.xls') or fname.lower().endswith('.xlsx'):
        return read_excel(fname, handler, sheet, *args, **kwds)
    else:
        raise ValueError('Unknown filetype: %s' % fname)


# Reading functions
def handle_rows(rows):
    """Store the rota information by name and job"""
    today = START_DAY
    on_call = {}

    for i, row in enumerate(rows):
        if row[0] == '0':
            row[0] = '10'
        try:
            if today.month == 12 and today.day == 31:
                today = date(today.year + 1, today.month, today.day)
            today = dateutil.parser.parse(row[0], default=today)
            if row[1] != '':
                if today in on_call:
                    print('Duplicate: ', today, row)
                else:
                    on_call[today] = (autocorrect(row[1]), row[2])
        except Exception:
            print('Weird row[', i, ']:', row)

    name_to_dates = defaultdict(list)

    for day in on_call:
        name, additional = on_call[day]
        name_to_dates[name].append((day, name, additional))
        name_to_dates['All'].append((day, name, additional))

    return name_to_dates


# Check last names functions
def check_last_names(names_to_dates, directory, between):
    """Check from the previous run of this parser if there are new names,
    returns a dictionary of names to number of rows"""
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
        for name in names_to_dates:
            # number is the sum of rows for each role for this name, job pair
            number = len([day for day, _, _ in names_to_dates[name]
                         if day >= between[0] and day < between[1]])
            if name not in last_names:
                # We have a new name
                print('New name in rota: %s with %d rows' % (name, number))
            w.writerow({'name': name, 'number': number})
            name_to_number_of_rows[name] = number

    return name_to_number_of_rows


# Writing functions
def create_calendars(names_to_dates, directory, between):
    from os.path import join
    for name in names_to_dates:
        dates = names_to_dates[name]
        cal = create_calendar_for(name, dates, between)
        with open(join(directory, 'rota_%s.ics' % (name)), 'wb') as f:
            f.write(cal.to_ical())


# Main function
def parse_file_and_create_calendars(fname, sheet, directory, between):
    from os.path import exists
    rows_data = read(fname, handle_rows, sheet)

    if not exists(directory):
        from os import makedirs
        makedirs(directory)
    check_last_names(rows_data, directory, between)
    create_calendars(rows_data, directory, between)


# __________________________________ MAIN ____________________________________
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Unusual-1 Rota reader')
    parser.add_argument('filename',
                        nargs='?',
                        help='the rota filename',
                        default='unusual1.xlsx')
    parser.add_argument('directory',
                        nargs='?',
                        help='output directory',
                        default='generated')
    parser.add_argument('--sheet',
                        nargs='?',
                        type=int,
                        help='excel spreadsheet id',
                        default=0)

    args = parser.parse_args()

    parse_file_and_create_calendars(args.filename,
                                    args.sheet,
                                    args.directory,
                                    BETWEEN)
