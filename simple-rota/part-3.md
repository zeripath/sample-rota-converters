# Simple Rota Reader 3 - Problems and Hosting

Great! We have a way of creating rota calendars for individual doctors. Albeit from a simple rota. But before we move on we should look at few potential issues.

## Hosting

There's no point creating these icalendar files if we can't get them into our applications.

We could post out the .ics files to everyone who wants them and then they import them directly into their calendar applications. A better plan would be to place the .ics files on a webserver somewhere, point our applications to that and then update the .ics files as needed.

A good place to put these would be on your own webserver - but you may not have one. Another good, free place is on http://github.io

## Date format

It's highly likely that your rota co-ordinator is not using a program to generate your rota, and that they're simply adjusting it by hand.

That means that they're likely to put dates in the file in various formats.

We've already put a few fallbacks in - but we should probably put a few others in.

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

Once we detect the abnormality we can adjust our code to cope with it. (Of course that hides a multitude of complexity.)

[Back](../)
