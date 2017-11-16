
# Name errors and other abuses

[HOME](https://zeripath.github.io/sample-rota-converters)

Back in [Part 3 of the Simple Rota](../simple-rota/part-3) we saw that it was likely that there would be errors in the data or special cases. For example take a look at [multi_rota3.xls](multi_rota3.xls):

* Spelling Mistakes like `Wiliam`
* Additional information like `James (instead of William)`
* Special cases like `James (AM) William (PM)`

We now have method to detect these but how do we fix these or cope with them?

## Spelling mistakes, Upper/Lower case and trailing spaces

Let's make two assumptions:

* It's fairly unlikely that two people on the same rota will get mispelled to the same thing.
* Once a spelling mistake has occurred, the same mistake is likely to happen again.
* The likelihood of the spelling mistake being fixed in a timely manner is low.

If these are true it's worth, once a spelling mistake has been detected, to add it to our program to autocorrect in future.

The simplest way to autocorrect these is to use a dictionary of incorrectly spelled names and their corrections - you could specify it by `job` if the corrections are different for different jobs, but lets keep it simple.


```python
SPELLING_CORRECTIONS = { 'Wiliam': 'William'}

def autocorrect(name):
    if name in SPELLING_CORRECTIONS:
        return SPELLING_CORRECTIONS[name]
    return name
```

But what about simple upper case/lower case mistakes, or even trailing spaces? 


```python
SPELLING_CORRECTIONS = { 'Wiliam'.lower().strip(): 'William'}

def autocorrect(name):
    canonical = name.lower().strip()
    if canonical in SPELLING_CORRECTIONS:
        return SPELLING_CORRECTIONS[canonical].title().strip()
    return canonical.title()

autocorrect(' WiliAM  ')
```




    'William'



Now we have to wire this autocorrecting code into `handle_rows`:

```python
def handle_rows(rows):
    """Store the rota information by name and job"""
    # nr_to_rows: name_to_list_of_rows_dict
    nr_to_rows = defaultdict(list)
    for row in rows:
        nr_to_rows[ ('All', 'All') ].append(row)
        for key in row:
            if key != 'Date':
                name = autocorrect(row[key])
                nr_to_rows[ (name, key) ].append(row)
    ...
```

We just have to keep adding spelling corrections as we see them.

* We could do better using an approach whereby we try to autocorrect  to already known names using phonetic/approximate matching of strings.  A number of methods are implemented in the jellyfish module <http://jellyfish.readthedocs.io/en/latest/> 

## Unecessary Additional Information

We have a number of options for dealing with additional information. A simple solution would be to place them in the spelling corrections directory as, and when, we see them. Another option is to match the type of string and strip out the correct name.

The easiest way to detect a string like `James (instead of William)` is to use `'(instead of' in test_string` and then `test_string[0:test_string.index('(instead of')`. However, if you have multiple strings to test for (e.g 'insted of') you may benefit from using a different scheme.

### Regular Expressions

Regular Expressions, or RegExps, are special strings describing a search pattern. You could call them wildcards on steroids. They are extremely useful tools and becoming proficient at using them is highly recommended - however, they can be a little arcane.


```python
import re

test_string = 'James (instead of William)'
test_string2 = 'James insted of Wiliam'
# ( ) <- marks a group
# . <- matches any character
# a* <- means a string of 'a' of any length
# \( <- means an actual open bracket
# a? <- means an optional 'a'
# a+ <- means 1 or more 'a's
# a*? <- means match the least number of 'a's necessary
re_string = '(.*?) \(?instea?d of .*' 

print(re.match(re_string, test_string).groups()[0])

re_compiled = re.compile(re_string)

print(re_compiled.match(test_string2).groups()[0])
```

    James
    James


Let's add a strip unnecessary information function to the autocorrect function.


```python
## Spelling corrections
import re
SPELLING_CORRECTIONS = { 'wiliam': 'William' }
UNNECESSARY_ADDITIONAL_INFORMATION_RES = [
    re.compile('(.*?) \(?instea?d of .*'),
    re.compile('(.*?) \(?not .*'),
    re.compile('(.*?) \(?replac.*'), # Catches x replacing y
]

def strip_unnecessary_information(name):
    canonical = name.lower().strip()
    for reg_exp in UNNECESSARY_ADDITIONAL_INFORMATION_RES:
        if reg_exp.match(canonical):
            canonical = reg_exp.match(canonical).groups()[0]
    return canonical

def autocorrect(name):
    canonical = strip_unnecessary_information(name)
    if canonical in SPELLING_CORRECTIONS:
        return SPELLING_CORRECTIONS[canonical].title().strip()
    return canonical.title()
```

## Special cases

So now we need to consider the `James (AM) William (PM)` case.

This is an interesting case because it means we need to put row into two names for the same role, and we'll need to catch it again in the `create_event_for` function.


```python
AM_PM_SPLIT_RE = re.compile('(.*) \(?(am)\)? (.*) \(?(pm)\)?')
def role_split(role_string):
    canonical = role_string.lower().strip()
    if AM_PM_SPLIT_RE.match(canonical):
        groups = AM_PM_SPLIT_RE.match(canonical).groups()
        return [groups[0], groups[2]]
    else:
        return [role_string]
    
def munge_role(name, role, row):
    canonical = row[role].lower().strip()
    if AM_PM_SPLIT_RE.match(canonical):
        groups = AM_PM_SPLIT_RE.match(canonical).groups()
        names = [autocorrect(groups[0]), autocorrect(groups[2])]
        if name in names:
            time_mod = groups[1 + names.index(name) * 2].upper()
            return (name, \
                    '{0} ({1})'.format(role, time_mod))
        
    return (name, role)
```

```python
## Reading functions
def handle_rows(rows):
    """Store the rota information by name and job"""
    # nr_to_rows: name_to_list_of_rows_dict
    nr_to_rows = defaultdict(list)
    for row in rows:
        nr_to_rows[ ('All', 'All') ].append(row)
        for key in row:
            if key != 'Date':
                names = role_split(row[key])
                for uncorrected in names:
                    name = autocorrect(uncorrected)
                    nr_to_rows[ (name, key) ].append(row)
    ...
```
```python
def create_event_for(name, role, row):
    """Create an icalendar event for this row for name and role"""
    event = Event()
    
    # Munge the role
    (name, role) = munge_role(name, role, row)
    ...
```

Finally we'll need to fix the `HOURS` dictionary to include appropriate times for the AM/PM switch.

```python
HOURS = {
    ...
    'SHO (AM)': {
        'start': time(8, tzinfo=TZ),
        'end': time(14, 0, tzinfo=TZ)
    },
    'SpR (AM)': {
        'start': time(8, tzinfo=TZ),
        'end': time(14, 0, tzinfo=TZ)
    },
    'SHO (PM)': {
        'start': time(14, tzinfo=TZ),
        'end': time(20, 30, tzinfo=TZ)
    },
    ...
}
```

[multi_rota3.py](multi_rota3.py)

[Back](../)
