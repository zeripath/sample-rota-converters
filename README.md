# Converting rotas into iCalendar files

[HOME](https://zeripath.github.io/sample-rota-converters)

## Rationale
Doctors in the UK often rotate jobs multiple times a year, and with each job
comes a new rota. A new rota in a new format, often complex, almost always
written as an excel spreadsheet, andupdated at random.

Almost every doctor has a mobile phone, on which there is a calendar
application. Some doctors will do the painstaking task of manually converting
that rota into events to be put on that application. Others will try to keep a
copy of it on their phones, and others will print the rota out and put it on
their wall.

We can do better.

## Why is manually converting rotas bad?

1. It's time consuming and repetitive - Humans are bad at doing this, but
   computers are good at this.
2. The rota will change and you will have to do that work again.
3. If you can do this for your rota - you can do it for everyone!

## What should we do?

Our calendar applications have a standard format for events, called the
`iCalendar` format - standard suffix `.ics`

This is defined at <https://icalendar.org>, wikipedia has a good description of
it <https://en.wikipedia.org/wiki/ICalendar>.

If we can convert our rotas to `.ics` files we can either import them into our
calendar applications, or, even better, stick them on a website and point our
applications to them so that they update automatically.

## Plan
* [Introduce the icalendar format](icalendar)
* Simple-Rota
  1. [Look at a very simple rota and write a simple converter](simple-rota/part-1)
  2. [Refine this converter](simple-rota/part-2)
  3. [Consider the problems of the converter](simple-rota/part-3)
* Multi-Rota
  1. [Multiple shift - multiple person rotas](multi-rota/part-1)
  2. [Adding night shifts to the multi-shift/multi-pers on rota](multi-rota/part-2)
  3. [Name errors and other abuses](multi-rota/part-3)
* Unusual-Rotas
  1. [A rota with an unusual date format](unusual-rotas/part-1)
