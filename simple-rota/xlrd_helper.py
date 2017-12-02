"""Functions and Classes to help make using an excel file easier.


This file provides two main classes: Reader and DictReader which are
reimplementations of their csv counterparts
"""
import xlrd
import mmap
from collections import OrderedDict

def cell_value_converter(cell, *args, **kwds):
    """Returns the value of a given cell."""
    return cell.value

def auto_converter(cell, book=None, date_format='%Y/%m/%d', *args, **kwds):
    """Converts a given cell to reasonable value using the provided date format for date cells."""
    if cell.ctype == 2:
        __v = cell.value
        return str(int(__v) if int(__v) == __v else __v)
    elif cell.ctype == 3:
        import datetime
        date_tuple = xlrd.xldate_as_tuple(cell.value, book.datemode)
        __d = datetime.datetime(*date_tuple)
        # Shortcut days to just print the way we expect
        if __d.hour == __d.minute == __d.second == 0:
            return __d.date().strftime(date_format)
        else:
            return __d.isoformat()
    else:
        return str(cell.value).strip()

class Reader:
    """ Provides a Reader object that will iterate over the rows in the given
    *excelfile*.  An optional *sheet_index* parameter for the sheet_index can
    be provided, as can a *converter* parameter to convert the cell to a useful
    value. The other optional *args and **fmtparams can be given to pass values
    to the converter.
    
    Each row from from the *excelfile* is returned as a list. The converter is
    run on each, and is passed the cell, and named parameters: sheet, book, i,
    and j in additional to the *args and **fmtparams.

    A short usage example::

    >>> import xlrd_helper
    >>> with open('eggs.xls') as excelfile:
    ...     spamreader = xlrd_helper.Reader(excelfile)
    ...     for row in spamreader:
    ...         print(', '.join(row))
    Spam, Spam, Spam, Spam, Baked Beans
    Spam, Lovely Spam, Wonderful Spam


    If cell is required rather than just the value a *converter* of `lambda x : x`
    will suffice.
    """

    def __init__(self, f, sheet_index=0, converter=auto_converter, *args, **kwargs):
        self.f = f
        self.sheet_index = sheet_index
        self.converter = converter
        self.data = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        self.book = xlrd.open_workbook(file_contents=self.data)
        self.sheet = self.book.sheet_by_index(sheet_index)
        self.row_num = 0
        self.args = args
        self.kwargs = kwargs

    def __iter__(self):
        for i, row in enumerate(self.sheet.get_rows()):
            self.row_num = i
            yield [ self.converter(cell,
                book=self.book,
                sheet=self.sheet,
                i=i,
                j=j,
                *self.args,
                **self.kwargs) for j, cell in enumerate(row) ]

class DictReader:
    """Creates an object that operates like a csv.DictReader but acting on an excel file.
    The information in each row will be mapped to an :mod: `OrderedDict <collections.OrderedDict>`
    whose keys are given by the optional *fieldnames* parameter.

    The *fieldnames* parameter is a :term: `sequence`. If *fieldnames* is omitted, the
    values in the first non-blank row of the excel sheet will be used as the fieldnames.

    If a row has more fields than fieldnames, the remaining data is placed in a list and
    stored with the fieldname specified by *restkey* (which defaults to ``None``). If a
    non-blank row has fewer fields than fieldnames, the missing values are filled with *restval* (which defaults to ``None``).

    All other optional or keyword arguments are passed to the underlying :class:`Reader` instance.

    A short usage example::

    >>> import xlrd_helper
    >>> with open('names.xls') as excelfile:
    ...     reader = xlrd_helper.DictReader(excelfile)
    ...     for row in reader:
    ...         print(row['first_name'], row['last_name'])
    Eric Idle
    John Cleese"""
    def __init__(self, f, fieldnames=None, restkey=None, restval=None, sheet_index=0, *args, **kwds):
        self._fieldnames = fieldnames
        self.restkey = restkey
        self.reader = Reader(f, sheet_index, *args, **kwds) 
        self.row_num = self.reader.row_num

    def __iter__(self):
        return self

    @property
    def fieldnames(self):
        self.row_num = self.reader.row_num
        return self._fieldnames
    
    @fieldnames.setter
    def fieldnames(self, value):
        self._fieldnames = value
        
    def __iter__(self):
        for row in self.reader:
            if row == []:
                pass
            self.row_num = self.reader.row_num
            if self.fieldnames is None:
                self._fieldnames = row
            else:
                d = OrderedDict(zip(self.fieldnames, row))
                len_fieldnames = len(self.fieldnames)
                len_row = len(row)
                if len_fieldnames < len_row:
                    d[self.restkey] = row[len_fieldnames:]
                elif len_fieldnames > len_row:
                    for key in self.fieldnames[len_row:]:
                        d[key] = self.restval
                yield d
