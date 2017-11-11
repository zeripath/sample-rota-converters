# Simple Rota Reader 3 - Problems and Hosting

[HOME](https://zeripath.github.io/sample-rota-converters)

Great! We have a way of creating rota calendars for individual doctors. Albeit from a simple rota. But before we move on we should look at few potential issues.

## Scripting vs. Testing

It would be helpful to restructure our file so that we can test individual functions in it using the python interpreter and can pass in arguments in like a normal program - for example a different filename.

If we wrap our main function code into a function, say `parse_file_and_create_calendars` and then use the `ArgumentParser` from the `argparse` module we can pass in default values.

Finally if we add an `if __name__ == '__main__':` block - this will only execute if we run the script directly.

```python
if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Simple Rota reader')
    parser.add_argument('filename', nargs='?', help='the rota filename', default='simple_rota.csv')
    parser.add_argument('directory', nargs='?', help='output directory', default='generated')
    parser.add_argument('--sheet', nargs='?', type=int, help='excel spreadsheet id', default=0)

    args = parser.parse_args()
    
    parse_file_and_create_calendars(args.filename, args.sheet, args.directory)
```

This will allow us to `import simple_rota3` our script into the interpreter and test functions. We can adjust our code and reload the code with:

```
>>> from importlib import reload
>>> reload(simple_rota3)
```

## Hosting

There's no point creating these icalendar files if we can't get them into our applications.

We could post out the .ics files to everyone who wants them and then they import them directly into their calendar applications. A better plan would be to place the .ics files on a webserver somewhere, point our applications to that and then update the .ics files as needed.

A good place to put these would be on your own webserver - but you may not have one. Another good, free place is on <http://github.io>

## Excel

Almost all rotas come as Excel files. Switching from reading excel files to csv files isn't a completely simple switch. There are two modules I know of that can read excel: `pandas` and `xlrd` but they both have different APIs to that of `csv`.

We'll use `xlrd` as it is the most simple. The basic reading code is as follows:


```python
try:
    import xlrd
except ModuleNotFoundError:
    !pip install --user xlrd

import xlrd

with xlrd.open_workbook('simple_rota.xls') as xls:
    sheet = xls.sheet_by_index(0)
    print('"%s", "%s"' % (sheet.cell_value(0, 0), sheet.cell_value(0, 1)))
```

    "Date", "On-Call"


There are a few gotchas though with this, data in Excel is typed and dates, times, date-times and integers are stored as floats which get converted by the GUI.

* The default formats for date etc. aren't even stored in the file - so when you pass an excel file to computer in a different locale - these will be displayed in their locale. Which is OK if Excel has auto-typed everything correctly but if not... (Say you have part numbers which have a '/' in them, every one that is a valid day/month pair or month/year pair will be autoconverted to a date unless you're very careful.)
* Another issue is that even when excel has typed things correctly there are many issues with these types:
 * Integers are not floating point - try: `=111111111 * 111111111 - 12345678987654300` and compare it with python's answer.
 * Decimals are not floating point - try: `=22.26 - 21.29`, (here python also gives the incorrect answer.)
 * There's no sensible way of dealing with daylight's saving time, let alone timezones.
 * I could go on but I'll just leave this one "date" here: 29 February 1900. 


```python
import xlrd

with xlrd.open_workbook('simple_rota.xls') as xls:
    sheet = xls.sheet_by_index(0)
    print('Cell value of (1, 0) is "%s"' % (sheet.cell_value(1, 0)))
    date_tuple = xlrd.xldate_as_tuple(sheet.cell_value(1, 0), xls.datemode)
    print('Which is actually: "%d/%02d/%02d %02d:%02d:%02d"' % date_tuple)
```

    Cell value of (1, 0) is "43101.0"
    Which is actually: "2018/01/01 00:00:00"


It would be ideal if there was a `DictReader` equivalent that did a sensible conversion for us... I've written a helper file for this: 
[xlrd_helper.py](xlrd_helper.py)


```python
import xlrd_helper

with open('simple_rota.xls', 'rb') as f:
    rows = xlrd_helper.DictReader(f)
    for row in rows:
        print(row)
        break
```

    OrderedDict([('Date', '2018/01/01'), ('On-Call', 'James')])


Note how the date is converted to `YYYY/MM/DD` format. Putting dates into year first format has a number of advantages, and I'd recommend this using year first formats rather that day first formats if you have any choice. (I'd recommend, however, you use `-` as separator or drop it altogether.)

* 4-digit year first formats are umambiguous - Whereas 01-02-18 is interpretted as 1st February 2018 in most of the world, it's 2nd January 2018 in the US, but could equally be 1918, or even 18th February 2001. 
* Further, these formats can be lexicographically sorted - so if you have them in a filename - then files will get sorted by date!

## Date format

It's highly likely that your rota co-ordinator is not using a program to generate your rota, and that they're simply adjusting it by hand.

That means that they're likely to put dates in the file in various formats.

One partial benefit of using Excel is that this becomes less of an issue as data in excel is typed. 

* Except of course when it isn't - you can input dates in to row and them not be automatically typed - so in order to make the rest of code easier I convert them to a string when I see them.


We've already put a few fallbacks in - and we could put a few others in - but there is another option: the `dateutil` module.


```python
try:
    import dateutil
except ModuleNotFoundError:
    !pip install dateutil

from dateutil.parser import parse

print(parse('February 1 2018', dayfirst=True))
print(parse('1 feb 2018', dayfirst=True))
print(parse('1/2/2018', dayfirst=True))
print(parse('01-02-18', dayfirst=True))
print(parse('2018.02.01', dayfirst=True), 
     parse('2018.02.01', dayfirst=True) == parse('01-02-18', dayfirst=True))
```

    2018-02-01 00:00:00
    2018-02-01 00:00:00
    2018-02-01 00:00:00
    2018-02-01 00:00:00
    2018-01-02 00:00:00 False


You see this fixes a number of problems, but note the use of `dayfirst`. As clever as this module is, it still cannot cope with the ambiguities of the 2 digit formats, and note that the last case fails!

## Name errors or other overloading of the names

As before your rota co-ordinator is likely going to be adjusting the rota by hand, and they're not going to be expected it to be read by a computer. This means we can expect:

* Spelling Mistakes like `Wiliam`
* Additional information like `James (instead of William)`
* Special cases like `James (AM) William (PM)`

But as things stand we'll just create new calendars for these and there will be a gap on the right person's calendar.

### How can we cope with this?

We can't predict what the rota co-ordinator is going to do, but what we should do is know when they've done something unusual.

### Detecting unusual behaviour

In the simple rota case we don't get told who is on the rota - the only way to work out who is on the rota is to look at it and parse it. That makes catching unusual behaviour a bit difficult, but we do have one way to catch it: Look at the last time we parsed the rota and complain if there are new "people" on the rota.

```python
last_names = {}
# Read the last names 
if exists('last_names_simple.csv'):
    with open('last_names_simple.csv') as f:
        r = DictReader(f)
        for row in r:
            last_names[row['name']] = int(row['number'])

with open('last_names_simple.csv', 'wb') as f:
    w = DictWriter(f, ['name', 'number'])
    w.writeheader()
    for name in name_to_list_of_rows_dict:
        number = len(name_to_list_of_rows_dict[name])
        if not name in last_names:
            # We have a new name
            print('New name in rota: %s with %d rows', (name, number))
        w.writerow( { 'name': name, 'number': number } )
```

Another option might be to detect the participants with very few on-calls and see if we can match them with others on the rota.

Once we detect the abnormality we can adjust our code to cope with it or try to match the abnormal name with name on the rota. (Of course that hides a multitude of complexity and we'll look at that later.)

That's probably enough for now so take a look at [simple_rota3.py](simple_rota3.py)

[Back](../)
