# Simple Rota Reader 2 - Individual rotas
OK, so now we have a way of producing the rotas for all people on the rota, why don't we try create rotas for the individual people on the rota?

Let's break the problem down in to steps:

1. Read the rows in and split them into individual doctors
2. For each doctor, create a calendar from their rows
3. Save each icalendar file for each doctor

Let's leave step 1 for the moment, but look at step 2.

## 2. Create a calendar from the doctor's rows
We just need to refactor create calendar code in to a function that takes some rows and returns a Calendar. (Whilst we're at it though we'll another parameter with a default for the title.)


```python
def create_calendar_for(rows, title='Simple Rota'):
    """Given a set of rows create a calendar for these rows"""
    cal = Calendar()

    # These two lines are required but you can change the prodid slightly
    cal.add('prodid', '-//hacksw/handcal/NONSGML v1.0//EN')
    cal.add('version', '2.0')

    # Set the title of the calendar, by default this is 'Simple Rota'
    cal.add('x-wr-calname', title)

    # Now create the events for each row
    for row in reader:
        event = create_event_for(row)
        cal.add_component(event)

    return cal
```

Let's step back to step 1.

* __Question:__ _Why don't I save the file in this function?_
* _the KISS (Keep It Simple, Stupid!) principle says do one thing at a time. This structure allows us to test the calendar or adjust the calendar later._

## 1. Read the rows and split them into individual doctors
OK so how can we go about this?

As we read the rows from the CSV file we want to store them in a data-structure that takes a name and returns a list of rows.

That's a simply a `dict` with `str` keys and a `list` values.

So let's try that:


```python
from csv import DictReader

name_to_list_of_rows_dict = {}

with open('simple_rota.csv') as f:
    r = DictReader(f)
    for row in r:
        name = row['On-Call']
        name_to_list_of_rows_dict[ name ].append(row)
        name_to_list_of_rows_dict[ 'All' ].append(row)
```


    ---------------------------------------------------------------------------

    KeyError                                  Traceback (most recent call last)

    <ipython-input-2-a155b05d5412> in <module>()
          7     for row in r:
          8         name = row['On-Call']
    ----> 9         name_to_list_of_rows_dict[ name ].append(row)
         10         name_to_list_of_rows_dict[ 'All' ].append(row)


    KeyError: 'James'


* **Oh dear! What does that mean?**

The error is in line 9 and it says that the `name_to_list_of_rows_dict` hasn't got a value for the key `'James'`. That's not really any clearer is it?

* **OK, let's step through this.**

The first time we reach line 9:

```
row = { 'Date': '01/01/2018', 'On-Call': 'James' }
name = 'James'
```

What is `name_to_list_of_rows_dict`? It's `{}`.

Is `'James' in {}`? No - it can't be and hence it's a `KeyError` to attempt to read its value.

* **How do we fix this?**

The first time we meet a new name we need to create an empty `list` so that we can `.append(...)` a row to it.


```python
from csv import DictReader

name_to_list_of_rows_dict = {}
name_to_list_of_rows_dict['All'] = []

with open('simple_rota.csv') as f:
    r = DictReader(f)
    for row in r:
        name = row['On-Call']
        if name not in name_to_list_of_rows_dict:
            name_to_list_of_rows_dict[name] = []
        name_to_list_of_rows_dict[ name ].append(row)
        name_to_list_of_rows_dict[ 'All' ].append(row)

print(name_to_list_of_rows_dict.keys())
```

    dict_keys(['All', 'James', 'Rebecca', 'William'])


Now that's a little ugly, can we do better?

What are we actually after is: [a dictionary where the default value is a list](https://www.google.co.uk/search?q=a%20dictionary%20where%20the%20default%20value%20is%20a%20list).

The first link on Google for that is https://stackoverflow.com/questions/17755996/python-list-as-default-value-for-dictionary

What it suggests is to use `collections.defaultdict`. Let's try that.


```python
from csv import DictReader
from collections import defaultdict

# Note that the definition uses list not list()
name_to_list_of_rows_dict = defaultdict(list)

with open('simple_rota.csv') as f:
    r = DictReader(f)
    for row in r:
        name = row['On-Call']
        name_to_list_of_rows_dict[ name ].append(row)
        name_to_list_of_rows_dict[ 'All' ].append(row)

print(name_to_list_of_rows_dict.keys())
```

    dict_keys(['James', 'All', 'Rebecca', 'William'])


## 3. Save a calendar for each doctor

So now, we have a way of getting each doctor's rows, and then creating a calendar for those rows. We need a way of saving the calendar.

Now in our last version of this we just saved the file as `simple-rota.ics`. We can't do that here, but we could save it as for example: `simple_rota_James.ics` in a similar manner as above. I'm going to use a [python format string](https://www.google.co.uk/search?q=python%20format%20string) for this, but you could just concatenate using `+`

```python
for name in name_to_list_of_rows_dict:
    rows = name_to_list_of_rows_dict[name]
    # To understand the below line Google: python format string
    cal = create_calendar_for(row, 'Simple Rota for %s' % name)
    with open('simple_rota_%s.ics' % name, 'wb') as f:
        f.write(cal.to_ical())
```

So now we can complete the updated [simple_rota2.py](simple_rota2.py)

[Back](../)
