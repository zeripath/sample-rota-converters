
# Unusual Rotas

[HOME](https://zeripath.github.io/sample-rota-converters)

All of our rota examples so far have had very reasonable date representations. Let's look at an another example [unusual1.xlsx](unusual1.xlsx):

| A | B | C |
|:---:|:---:|:---:|
| OCT |  |  |
| 1 | SpR3 |  |
| 2 | SpR1 |  |
| 3 | SpR6(JR) | SpR5 doing 5th Oct |
| 4 | SpR2 |  |
| 5 | SpR5 | SpR6 doing 3rd Oct |
| 6 | SpR3 |  |
| 7 | SpR2 | SpR4 doing 4th Nov  |
| 8 | SpR2 | SpR4 doing 5th Nov  |
| 9 | SpR5 |  |
| 10 | SpR2 |  |
| 11 | SpR4 | SpR6 doing 3 Nov |
| 12 | SpR3 |  |
| 13 | SpR2 | SpR4 doing 11 Oct |
| 14 | SpR1 |  |
| 15 | SpR1 |  |
| 16 | SpR2 |  |
| 17 | SpR6 |  |
| 18 | SpR3 |  |
| 19 | SpR4 |  |
| 20 | SpR6 | SpR1 doing 3rd November |
| 21 | SpR5 |  |
| 22 | SpR5 |  |
| 23 | SpR3 |  SpR6 Doing 24 oct |
| 24 | SpR6 | SpR3 doing 23rd Oct |
| 25 | SpR4 |  |
| 26 | SpR1 |  |
| 27 | SpR5 |  |
| 28 | SpR2 |  |
| 29 | SpR2 |  |
| 30 | SpR5 | UCH 3 doing |
| 31 | SpR4 |  |
| NOV |  |  |
| 1 | SpR1 |  |

## First steps - loading the rota
OK, so how do we deal with a rota like this...? Let's first try loading it and see what we've got...


```python
from xlrd_helper import DictReader
rows = []

with open('unusual1.xlsx', 'rb') as f:
    rows = [ row for row in DictReader(f)]
    print(rows[0].keys())
    print(rows[0])
```

    odict_keys(['Jun', ''])
    OrderedDict([('Jun', '1'), ('', '')])


Now looking carefully we see that the fieldnames aren't quite right, (neither is the data quite what we were expecting either - but we'll get to that). It turns out that this rota doesn't have headers. 

We have two options: We can drop down to using the Reader implementation or we could pass in some fieldnames. Let's look at passing in some fieldnames. I'll also pass in a `restkey` which will allow us to pick up anything placed in other columns.


```python
from xlrd_helper import DictReader
rows = []
fieldnames = ['date', 'oncall', 'additional']

with open('unusual1.xlsx', 'rb') as f:
    rows = [ row for row in DictReader(f, fieldnames=fieldnames, 
                                      restkey='other')]
    print(rows[0].keys())
    print(rows[0])
```

    odict_keys(['date', 'oncall', 'additional', 'other'])
    OrderedDict([('date', 'Jun'), ('oncall', ''), ('additional', ''), ('other', ['', '', '', ''])])


Now, let's go back to why the first piece of data is 'Jun' when we were expecting 'Oct'...

It turns out that if you look at the excel file, the first 503 rows are hidden. Getting the information about hidden rows requires adding a few options to the `DictReader` and querying the workbook ourselves,


```python
from xlrd_helper import DictReader
rows = []
fieldnames = ['date', 'oncall', 'additional']

try:
    with open('unusual1.xlsx', 'rb') as f:
        dr = DictReader(f, fieldnames=fieldnames, restkey='other', formatting_info=True)
        rows = [ row for row in dr]
        print(rows[0].keys())
        print(rows[0])
        print(dr.reader.sheet.rowinfo_map)
except NotImplementedError:
    print('Formatting info not implemented in xlrd for XLSX')
```

    Formatting info not implemented in xlrd for XLSX


Now, it turns out there is another package out there for doing this: `openpyxl`. However, we should probably consider whether we want to go down this path... If the rota co-ordinator is just hiding rows then it means that the starting point for the file is unlikely to change - whereas the first hidden row is likely to change. 

So thinking on we probably don't need to know whether a row is hidden or not. (It may be helpful in future though.)


## Looking at the first column
Let's look at the contents of the first column.


```python
from xlrd_helper import DictReader

fieldnames = ['date', 'oncall', 'additional']

with open('unusual1.xlsx', 'rb') as f:
    dr = DictReader(f, fieldnames=fieldnames, restkey='other')
    rows = [ row for row in dr ]
    dates = [ row['date'] for row in rows]

print(dates)
```

    ['Jun', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', 'Jul', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', 'Aug', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', 'Sept', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', 'Oct', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', 'Nov', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', 'Dec', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', 'jAN', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', 'FEB', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', 'MAR', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', 'APR', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', 'MAY', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', 'JUN', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', 'JUL', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', 'AUG', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', 'SEP', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', 'OCT', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', 'NOV', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', 'DEC', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '2018', '2018/01/01', '2018/01/02', '2018/01/03', '2018/01/04', '2018/01/05', '2018/01/06', '2018/01/07', '2018/01/08', '2018/01/09', '2018/01/10', '2018/01/11', '2018/01/12', '2018/01/13', '2018/01/14', '2018/01/15', '2018/01/16', '2018/01/17', '2018/01/18', '2018/01/19', '2018/01/20', '2018/01/21', '2018/01/22', '2018/01/23', '2018/01/24', '2018/01/25', '2018/01/26', '2018/01/27', '2018/01/28', '2018/01/29', '2018/01/30', '2018/01/31', '2018/02/01', '2018/02/02', '2018/02/03', '2018/02/04', '2018/02/05', '2018/02/06', '2018/02/07', '2018/02/08', '2018/02/09', '2018/02/10', '2018/02/11', '2018/02/12', '2018/02/13', '2018/02/14', '2018/02/15', '2018/02/16', '2018/02/17', '2018/02/18', '2018/02/19', '2018/02/20', '2018/02/21', '2018/02/22', '2018/02/23', '2018/02/24', '2018/02/25', '2018/02/26', '2018/02/27', '2018/02/28', '2018/03/01', '2018/03/02', '2018/03/03', '2018/03/04', '2018/03/05', '2018/03/06', '2018/03/07', '2018/03/08', '2018/03/09', '2018/03/10', '2018/03/11', '2018/03/12', '2018/03/13', '2018/03/14', '2018/03/15', '2018/03/16', '2018/03/17', '2018/03/18', '2018/03/19', '2018/03/20', '2018/03/21', '2018/03/22', '2018/03/23', '2018/03/24', '2018/03/25', '2018/03/26', '2018/03/27', '2018/03/28', '2018/03/29', '2018/03/30', '2018/03/31', '2018/04/01', '2018/04/02', '2018/04/03', '2018/04/04', '2018/04/05', '2018/04/06', '2018/04/07', '2018/04/08', '2018/04/09', '2018/04/10', '2018/04/11', '2018/04/12', '2018/04/13', '2018/04/14', '2018/04/15', '2018/04/16', '2018/04/17', '2018/04/18', '2018/04/19', '2018/04/20', '2018/04/21', '2018/04/22', '2018/04/23', '2018/04/24', '2018/04/25', '2018/04/26', '2018/04/27', '2018/04/28', '2018/04/29', '2018/04/30', '2018/05/01', '2018/05/02', '2018/05/03', '2018/05/04', '2018/05/05', '2018/05/06', '2018/05/07', '2018/05/08', '2018/05/09', '2018/05/10', '2018/05/11', '2018/05/12', '2018/05/13', '2018/05/14', '2018/05/15', '2018/05/16', '2018/05/17', '2018/05/18', '2018/05/19', '2018/05/20', '2018/05/21', '2018/05/22', '2018/05/23', '2018/05/24', '2018/05/25', '2018/05/26', '2018/05/27', '2018/05/28', '2018/05/29', '2018/05/30', '2018/05/31', '2018/06/01', '2018/06/02', '2018/06/03', '2018/06/04', '2018/06/05', '2018/06/06', '2018/06/07', '2018/06/08', '2018/06/09', '2018/06/10', '2018/06/11', '2018/06/12', '2018/06/13', '2018/06/14', '2018/06/15', '2018/06/16', '2018/06/17', '2018/06/18', '2018/06/19', '2018/06/20', '2018/06/21', '2018/06/22', '2018/06/23', '2018/06/24', '2018/06/25', '2018/06/26', '2018/06/27', '2018/06/28', '2018/06/29', '2018/06/30', '2018/07/01', '2018/07/02', '2018/07/03', '2018/07/04', '2018/07/05', '2018/07/06', '2018/07/07', '2018/07/08', '2018/07/09', '2018/07/10', '2018/07/11', '2018/07/12', '2018/07/13', '2018/07/14', '2018/07/15', '2018/07/16', '2018/07/17', '2018/07/18', '2018/07/19', '2018/07/20', '2018/07/21', '2018/07/22', '2018/07/23', '2018/07/24', '2018/07/25', '2018/07/26', '2018/07/27', '2018/07/28', '2018/07/29', '2018/07/30', '2018/07/31', '2018/08/01', '2018/08/02', '2018/08/03', '2018/08/04', '2018/08/05', '2018/08/06', '2018/08/07', '2018/08/08', '2018/08/09', '2018/08/10', '2018/08/11', '2018/08/12', '2018/08/13', '2018/08/14', '2018/08/15', '2018/08/16', '2018/08/17', '2018/08/18', '2018/08/19', '2018/08/20', '2018/08/21', '2018/08/22', '2018/08/23', '2018/08/24', '2018/08/25', '2018/08/26', '2018/08/27', '2018/08/28', '2018/08/29', '2018/08/30', '2018/08/31', '2018/09/01', '2018/09/02', '2018/09/03', '2018/09/04', '2018/09/05', '2018/09/06', '2018/09/07', '2018/09/08', '2018/09/09', '2018/09/10', '2018/09/11', '2018/09/12', '2018/09/13', '2018/09/14', '2018/09/15', '2018/09/16', '2018/09/17', '2018/09/18', '2018/09/19', '2018/09/20', '2018/09/21', '2018/09/22', '2018/09/23', '2018/09/24', '2018/09/25', '2018/09/26', '2018/09/27', '2018/09/28', '2018/09/29', '2018/09/30', '2018/10/01', '2018/10/02', '2018/10/03', '2018/10/04', '2018/10/05', '2018/10/06', '2018/10/07', '2018/10/08', '2018/10/09', '2018/10/10', '2018/10/11', '2018/10/12', '2018/10/13', '2018/10/14', '2018/10/15', '2018/10/16', '2018/10/17', '2018/10/18', '2018/10/19', '2018/10/20', '2018/10/21', '2018/10/22', '2018/10/23', '2018/10/24', '2018/10/25', '2018/10/26', '2018/10/27', '2018/10/28', '2018/10/29', '2018/10/30', '2018/10/31', '2018/11/01', '2018/11/02', '2018/11/03', '2018/11/04', '2018/11/05', '2018/11/06', '2018/11/07', '2018/11/08', '2018/11/09', '2018/11/10', '2018/11/11', '2018/11/12', '2018/11/13', '2018/11/14', '2018/11/15', '2018/11/16', '2018/11/17', '2018/11/18', '2018/11/19', '2018/11/20', '2018/11/21', '2018/11/22', '2018/11/23', '2018/11/24', '2018/11/25', '2018/11/26', '2018/11/27', '2018/11/28', '2018/11/29', '2018/11/30', '2018/12/01', '2018/12/02', '2018/12/03', '2018/12/04', '2018/12/05', '2018/12/06', '2018/12/07', '2018/12/08', '2018/12/09', '2018/12/10', '2018/12/11', '2018/12/12', '2018/12/13', '2018/12/14', '2018/12/15', '2018/12/16', '2018/12/17', '2018/12/18', '2018/12/19', '2018/12/20', '2018/12/21', '2018/12/22', '2018/12/23', '2018/12/24', '2018/12/25', '2018/12/26', '2018/12/27', '2018/12/28', '2018/12/29', '2018/12/30', '2018/12/31', '2019', '2019/01/01', '2019/01/02', '2019/01/03', '2019/01/04', '2019/01/05', '2019/01/06', '2019/01/07', '2019/01/08', '2019/01/09', '2019/01/10', '2019/01/11', '2019/01/12', '2019/01/13', '2019/01/14', '2019/01/15', '2019/01/16', '2019/01/17', '2019/01/18', '2019/01/19', '2019/01/20', '2019/01/21', '2019/01/22', '2019/01/23', '2019/01/24', '2019/01/25', '2019/01/26', '2019/01/27', '2019/01/28', '2019/01/29', '2019/01/30', '2019/01/31', '2019/02/01', '2019/02/02', '2019/02/03', '2019/02/04', '2019/02/05', '2019/02/06', '2019/02/07', '2019/02/08', '2019/02/09', '2019/02/10', '2019/02/11', '2019/02/12', '2019/02/13', '2019/02/14', '2019/02/15', '2019/02/16', '2019/02/17', '2019/02/18', '2019/02/19', '2019/02/20', '2019/02/21', '2019/02/22', '2019/02/23', '2019/02/24']


There are 4 things in there: a month indicator, a day, a year indicator, or a date


```python
import re 
day_match = re.compile('^\d\d?$')
year_match = re.compile('^\d\d\d\d$')
date_match = re.compile('^\d\d\d\d/\d\d/\d\d$')
days, years, actual_dates, others = [], [], [], []
for i, d in enumerate(dates):
    if day_match.match(d):
        days.append((i, d))
    elif year_match.match(d):
        years.append((i, d))
    elif date_match.match(d):
        actual_dates.append((i, d))
    else:
        others.append((i, d))

print ('No. of days:\t%3d' % len(days))
print ('No. of years:\t%3d' % len(years))
print ('No. of dates:\t%3d' % len(actual_dates))
print ('Others:\t\t%3d' % len(others))
```

    No. of days:	579
    No. of years:	  2
    No. of dates:	420
    Others:		 19


So we should just check those others and make sure that they actually are months and whilst we are at it let's check that there is only on-call information in the rows that have days or dates.


```python
for i, o in others:
    print (i, o)
    
print(all((all((rows[i]['oncall'] == '' for i,_ in others)),
           all((rows[i]['oncall'] == '' for i,_ in years)),
           all((rows[i]['oncall'] != '' for i,_ in days)),
           all((rows[i]['oncall'] != '' for i,_ in actual_dates)))))
```

    0 Jun
    31 Jul
    63 Aug
    95 Sept
    126 Oct
    158 Nov
    189 Dec
    221 jAN
    253 FEB
    282 MAR
    314 APR
    345 MAY
    377 JUN
    408 JUL
    440 AUG
    472 SEP
    503 OCT
    535 NOV
    566 DEC
    True


## Parsing the first column
How can we parse this? Either, the row contains an actual date, or it's one of the following: A year, a month or a day. So if we have a good idea of the preceding date we can just adjust our date and in fact `dateutil.parser.parse` will interpret a given date string in the context of another default date.

Looking at the column data carefully we can see that the first row refers to June 2016. We could work backwards from the dates but let's go forwards for the moment, so let's set the our default date as June 1st 2016.


```python
from datetime import date

from dateutil.parser import parse

oncall = {}

today = date(2016, 6, 1)
for i, row in enumerate(rows):
    d = row['date']
    c = row['oncall']
    a = row['additional']

    # Parse our new date in the context of the previous date
    today = parse(d, default=today)
    
    # If we're setting an oncall person
    if c != '':
        if today in oncall:
            print('Duplicate: ', today, i, d)
        else:
            oncall[today] = (c, a)
```


    ---------------------------------------------------------------------------

    ValueError                                Traceback (most recent call last)

    <ipython-input-8-8862ff80279a> in <module>()
         12 
         13     # Parse our new date in the context of the previous date
    ---> 14     today = parse(d, default=today)
         15 
         16     # If we're setting an oncall person


    /usr/local/lib/python3.6/dist-packages/dateutil/parser.py in parse(timestr, parserinfo, **kwargs)
       1180         return parser(parserinfo).parse(timestr, **kwargs)
       1181     else:
    -> 1182         return DEFAULTPARSER.parse(timestr, **kwargs)
       1183 
       1184 


    /usr/local/lib/python3.6/dist-packages/dateutil/parser.py in parse(self, timestr, default, ignoretz, tzinfos, **kwargs)
        579                 repl['day'] = monthrange(cyear, cmonth)[1]
        580 
    --> 581         ret = default.replace(**repl)
        582 
        583         if res.weekday is not None and not res.day:


    ValueError: day is out of range for month


Now that's strange... How did that happened? Let's catch that error and add some logging:


```python
from datetime import date

from dateutil.parser import parse

oncall = {}

today = date(2016, 6, 1)
for i, row in enumerate(rows):
    d = row['date']
    c = row['oncall']
    a = row['additional']

    try:
        # Parse our new date in the context of the previous date
        yesterday = today
        today = parse(d, default=yesterday)

        # If we're setting an oncall person
        if c != '':
            if today in oncall:
                print('Duplicate: ', today, i, d)
            else:
                oncall[today] = (c, a)
    except ValueError as e:
        print(e)
        print('Row %d with day value: %s, (Value Above: %s, Below: %s)' % (i, d, rows[i -1]['date'], rows[i + 1]['date']))
        
```

    day is out of range for month
    Row 10 with day value: 0, (Value Above: 9, Below: 11)
    day is out of range for month
    Row 41 with day value: 0, (Value Above: 9, Below: 11)
    day is out of range for month
    Row 73 with day value: 0, (Value Above: 9, Below: 11)
    day is out of range for month
    Row 105 with day value: 0, (Value Above: 9, Below: 11)
    day is out of range for month
    Row 136 with day value: 0, (Value Above: 9, Below: 11)
    Duplicate:  2016-06-01 378 1
    Duplicate:  2016-06-02 379 2
    Duplicate:  2016-06-03 380 3
    Duplicate:  2016-06-04 381 4
    Duplicate:  2016-06-05 382 5
    Duplicate:  2016-06-06 383 6
    Duplicate:  2016-06-07 384 7
    Duplicate:  2016-06-08 385 8
    Duplicate:  2016-06-09 386 9
    Duplicate:  2016-06-11 388 11
    Duplicate:  2016-06-12 389 12
    Duplicate:  2016-06-13 390 13
    Duplicate:  2016-06-14 391 14
    Duplicate:  2016-06-15 392 15
    Duplicate:  2016-06-16 393 16
    Duplicate:  2016-06-17 394 17
    Duplicate:  2016-06-18 395 18
    Duplicate:  2016-06-19 396 19
    Duplicate:  2016-06-20 397 20
    Duplicate:  2016-06-21 398 21
    Duplicate:  2016-06-22 399 22
    Duplicate:  2016-06-23 400 23
    Duplicate:  2016-06-24 401 24
    Duplicate:  2016-06-25 402 25
    Duplicate:  2016-06-26 403 26
    Duplicate:  2016-06-27 404 27
    Duplicate:  2016-06-28 405 28
    Duplicate:  2016-06-29 406 29
    Duplicate:  2016-06-30 407 30
    Duplicate:  2016-07-01 409 1
    Duplicate:  2016-07-02 410 2
    Duplicate:  2016-07-03 411 3
    Duplicate:  2016-07-04 412 4
    Duplicate:  2016-07-05 413 5
    Duplicate:  2016-07-06 414 6
    Duplicate:  2016-07-07 415 7
    Duplicate:  2016-07-08 416 8
    Duplicate:  2016-07-09 417 9
    Duplicate:  2016-07-11 419 11
    Duplicate:  2016-07-12 420 12
    Duplicate:  2016-07-13 421 13
    Duplicate:  2016-07-14 422 14
    Duplicate:  2016-07-15 423 15
    Duplicate:  2016-07-16 424 16
    Duplicate:  2016-07-17 425 17
    Duplicate:  2016-07-18 426 18
    Duplicate:  2016-07-19 427 19
    Duplicate:  2016-07-20 428 20
    Duplicate:  2016-07-21 429 21
    Duplicate:  2016-07-22 430 22
    Duplicate:  2016-07-23 431 23
    Duplicate:  2016-07-24 432 24
    Duplicate:  2016-07-25 433 25
    Duplicate:  2016-07-26 434 26
    Duplicate:  2016-07-27 435 27
    Duplicate:  2016-07-28 436 28
    Duplicate:  2016-07-29 437 29
    Duplicate:  2016-07-30 438 30
    Duplicate:  2016-07-31 439 31
    Duplicate:  2016-08-01 441 1
    Duplicate:  2016-08-02 442 2
    Duplicate:  2016-08-03 443 3
    Duplicate:  2016-08-04 444 4
    Duplicate:  2016-08-05 445 5
    Duplicate:  2016-08-06 446 6
    Duplicate:  2016-08-07 447 7
    Duplicate:  2016-08-08 448 8
    Duplicate:  2016-08-09 449 9
    Duplicate:  2016-08-11 451 11
    Duplicate:  2016-08-12 452 12
    Duplicate:  2016-08-13 453 13
    Duplicate:  2016-08-14 454 14
    Duplicate:  2016-08-15 455 15
    Duplicate:  2016-08-16 456 16
    Duplicate:  2016-08-17 457 17
    Duplicate:  2016-08-18 458 18
    Duplicate:  2016-08-19 459 19
    Duplicate:  2016-08-20 460 20
    Duplicate:  2016-08-21 461 21
    Duplicate:  2016-08-22 462 22
    Duplicate:  2016-08-23 463 23
    Duplicate:  2016-08-24 464 24
    Duplicate:  2016-08-25 465 25
    Duplicate:  2016-08-26 466 26
    Duplicate:  2016-08-27 467 27
    Duplicate:  2016-08-28 468 28
    Duplicate:  2016-08-29 469 29
    Duplicate:  2016-08-30 470 30
    Duplicate:  2016-08-31 471 31
    Duplicate:  2016-09-01 473 1
    Duplicate:  2016-09-02 474 2
    Duplicate:  2016-09-03 475 3
    Duplicate:  2016-09-04 476 4
    Duplicate:  2016-09-05 477 5
    Duplicate:  2016-09-06 478 6
    Duplicate:  2016-09-07 479 7
    Duplicate:  2016-09-08 480 8
    Duplicate:  2016-09-09 481 9
    Duplicate:  2016-09-11 483 11
    Duplicate:  2016-09-12 484 12
    Duplicate:  2016-09-13 485 13
    Duplicate:  2016-09-14 486 14
    Duplicate:  2016-09-15 487 15
    Duplicate:  2016-09-16 488 16
    Duplicate:  2016-09-17 489 17
    Duplicate:  2016-09-18 490 18
    Duplicate:  2016-09-19 491 19
    Duplicate:  2016-09-20 492 20
    Duplicate:  2016-09-21 493 21
    Duplicate:  2016-09-22 494 22
    Duplicate:  2016-09-23 495 23
    Duplicate:  2016-09-24 496 24
    Duplicate:  2016-09-25 497 25
    Duplicate:  2016-09-26 498 26
    Duplicate:  2016-09-27 499 27
    Duplicate:  2016-09-28 500 28
    Duplicate:  2016-09-29 501 29
    Duplicate:  2016-09-30 502 30
    Duplicate:  2016-10-01 504 1
    Duplicate:  2016-10-02 505 2
    Duplicate:  2016-10-03 506 3
    Duplicate:  2016-10-04 507 4
    Duplicate:  2016-10-05 508 5
    Duplicate:  2016-10-06 509 6
    Duplicate:  2016-10-07 510 7
    Duplicate:  2016-10-08 511 8
    Duplicate:  2016-10-09 512 9
    Duplicate:  2016-10-11 514 11
    Duplicate:  2016-10-12 515 12
    Duplicate:  2016-10-13 516 13
    Duplicate:  2016-10-14 517 14
    Duplicate:  2016-10-15 518 15
    Duplicate:  2016-10-16 519 16
    Duplicate:  2016-10-17 520 17
    Duplicate:  2016-10-18 521 18
    Duplicate:  2016-10-19 522 19
    Duplicate:  2016-10-20 523 20
    Duplicate:  2016-10-21 524 21
    Duplicate:  2016-10-22 525 22
    Duplicate:  2016-10-23 526 23
    Duplicate:  2016-10-24 527 24
    Duplicate:  2016-10-25 528 25
    Duplicate:  2016-10-26 529 26
    Duplicate:  2016-10-27 530 27
    Duplicate:  2016-10-28 531 28
    Duplicate:  2016-10-29 532 29
    Duplicate:  2016-10-30 533 30
    Duplicate:  2016-10-31 534 31
    Duplicate:  2016-11-01 536 1
    Duplicate:  2016-11-02 537 2
    Duplicate:  2016-11-03 538 3
    Duplicate:  2016-11-04 539 4
    Duplicate:  2016-11-05 540 5
    Duplicate:  2016-11-06 541 6
    Duplicate:  2016-11-07 542 7
    Duplicate:  2016-11-08 543 8
    Duplicate:  2016-11-09 544 9
    Duplicate:  2016-11-10 545 10
    Duplicate:  2016-11-11 546 11
    Duplicate:  2016-11-12 547 12
    Duplicate:  2016-11-13 548 13
    Duplicate:  2016-11-14 549 14
    Duplicate:  2016-11-15 550 15
    Duplicate:  2016-11-16 551 16
    Duplicate:  2016-11-17 552 17
    Duplicate:  2016-11-18 553 18
    Duplicate:  2016-11-19 554 19
    Duplicate:  2016-11-20 555 20
    Duplicate:  2016-11-21 556 21
    Duplicate:  2016-11-22 557 22
    Duplicate:  2016-11-23 558 23
    Duplicate:  2016-11-24 559 24
    Duplicate:  2016-11-25 560 25
    Duplicate:  2016-11-26 561 26
    Duplicate:  2016-11-27 562 27
    Duplicate:  2016-11-28 563 28
    Duplicate:  2016-11-29 564 29
    Duplicate:  2016-11-30 565 30
    Duplicate:  2016-12-01 567 1
    Duplicate:  2016-12-02 568 2
    Duplicate:  2016-12-03 569 3
    Duplicate:  2016-12-04 570 4
    Duplicate:  2016-12-05 571 5
    Duplicate:  2016-12-06 572 6
    Duplicate:  2016-12-07 573 7
    Duplicate:  2016-12-08 574 8
    Duplicate:  2016-12-09 575 9
    Duplicate:  2016-12-10 576 10
    Duplicate:  2016-12-11 577 11
    Duplicate:  2016-12-12 578 12
    Duplicate:  2016-12-13 579 13
    Duplicate:  2016-12-14 580 14
    Duplicate:  2016-12-15 581 15
    Duplicate:  2016-12-16 582 16
    Duplicate:  2016-12-17 583 17
    Duplicate:  2016-12-18 584 18
    Duplicate:  2016-12-19 585 19
    Duplicate:  2016-12-20 586 20
    Duplicate:  2016-12-21 587 21
    Duplicate:  2016-12-22 588 22
    Duplicate:  2016-12-23 589 23
    Duplicate:  2016-12-24 590 24
    Duplicate:  2016-12-25 591 25
    Duplicate:  2016-12-26 592 26
    Duplicate:  2016-12-27 593 27
    Duplicate:  2016-12-28 594 28
    Duplicate:  2016-12-29 595 29
    Duplicate:  2016-12-30 596 30
    Duplicate:  2016-12-31 597 31


The observant will have noticed that for some reason there are a couple of rows which have `0` instead of `10`. There's no other `0`s in the column.

Now understanding the duplicates requires a bit more thought. The first duplicate is in row 378 and the last duplicate is interpreted as 2016-12-31 in row 597. Now row 598 is `2018` - so I think we're not getting the change of year right. Let's look at what's supposed to happen when go over the year.


```python
today = date(2016, 12, 31)
print(parse('Jan', default=today))
```

    2016-01-31


Which obviously doesn't work. We'll just have to catch this case and manage the changeover ourselves.


```python
from dateutil.parser import parse

oncall = {}

today = date(2016, 6, 1)
for i, row in enumerate(rows):
    d = row['date']
    c = row['oncall']
    a = row['additional']

    try:
        # Parse our new date in the context of the previous date
        yesterday = today
        if d == '0':
            d = '10'
        if today.month == 12 and today.day == 31:
            today = date(today.year + 1, today.month, today.day)
        today = parse(d, default=today)

        # If we're setting an oncall person
        if c != '':
            if today in oncall:
                print('Duplicate: ', today, i, d)
            else:
                oncall[today] = (c, a)
    except ValueError as e:
        print(e)
        print('Row %d with day value: %s, (Value Above: %s, Below: %s)' % (i, d, rows[i -1]['date'], rows[i + 1]['date']))

```

## Other considerations
The whole rota runs from 2016-2018. Obviously, it's not much help for us to have a rota for the whole of that range, so we would need to set some starting and end dates for the range. We may aswell have these hardcoded for the moment, but it's not hard to think of a way to pass these in as a parameter if you want.

## Creating the rota
So we could create a new reader from scratch, or we could instead adjust one of our previous readers. It's simpler to just adjust an old reader so let's do that.

Let's recall the strcture of the multi_rota3.py:

```python
### IMPORTS
...
### CONSTANTS
...
HOURS = { ... }
...
### FUNCTIONS
...
SPELLING_CORRECTIONS = { ... }
UNNECESSARY_ADDITIONAL_INFORMATION_RES = [ ... ]

def strip_unnecessary_information(name):
    ...

def autocorrect(name):
    ...

AM_PM_SPLIT_RE = re.compile('(.*) \(?(am)\)? (.*) \(?(pm)\)?')
def role_split(role_string):
    ...

def munge_role(name, role, row):
    ...

## Conversion functions 
def convert_to_date(date_str):
    ...

## Calendar functions
def create_calendar_for(name, job, role_rows_list):
    ...

def create_event_for(name, role, row):
    ...

## File reading functions
def read_csv(fname, handler, sheet, *args, **kwds):
    ...
                            
def read_excel(fname, handler, sheet=0, *args, **kwds):
    ...

def read(fname, handler, sheet=0, *args, **kwds):
    ...
                            
## Reading functions
def handle_rows(rows):
    ...

## Check last names functions
def check_last_names(nj_to_r_rows, directory):
    ...
                            
## Writing functions
def create_calendars(nj_to_r_rows, directory):
    ...

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
   ...
```

### `HOURS`
This is simple, our shifts are all day in this case

```python
HOURS = {
    'On-Call': {
        'duration': timedelta(days=1)
    },
}
```

### `BETWEEN` and `START_DAY`
We should add a default `BETWEEN` and `START_DAY`. 

```python
BETWEEN = (date(2017, 12, 6), date(2018, 3, 7))

START_DAY = date(2016,1,1)
```

### `SPELLING_CORRECTIONS` and `munge_role` etc.
We don't need to keep any of the role munging functions as there's no roles in this rota. We can probably keep the spelling correction functions as these may come in handy.

### `convert_to_date`
If we think about the way we parsed the rota above we already did the conversion - so we don't need this function either. (Of course we'll have to adjust any code that uses it.)

### `create_calendar_for`, `create_event_for` and `handle_rows`
In multi_rota3.py `handle_rows` returns a dictionary of name job pairs to a list of role and rows pairs. Previous iterations had a dictionary of name to rows.

Our above code creates a dictionary of dates to person on-call - so in order to keep it a simple change we should create a dictionary of name to list of days on-call with additional information.


```python
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
```

Which means we can change our `create_calendar_for` function to:


```python
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
```

Finally we have to adjust the `create_event_for` method.


```python
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

```

### `check_last_names`
We'll have to adjust `check_last_names` to be more like the simpler version in multi_rota1.py - but otherwise it's a simple copy.


```python
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
```

So if we put all those things in to a rota reader we get a working rota reader for the unusual rota [unusual1.py](unusual1.py)
[Back](../)
