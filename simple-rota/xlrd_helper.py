"""Functions to help make using an excel file easier"""
import xlrd
import mmap
from collections import OrderedDict

def cell_value_converter(sheet, i, j, *args):
    """For a given sheet and co-ords return the cell's value"""
    return sheet.cell_value(i, j)

def cell_converter(sheet, i, j, *args):
    """For a given sheet and co-ords return the cell"""
    return sheet.cell(i, j)

def auto_converter(sheet, i, j, book, date_format='%Y/%m/%d'):
    """For a given sheet and co-ords return a sensible string representation of the value"""
    cell = sheet.cell(i, j)
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
        return self
        
    def __next__(self):
        if self.row_num < self.sheet.nrows:
            row = [self.converter(self.sheet, self.row_num, j, self.book, *self.args, **self.kwargs) \
                    for j in range(self.sheet.ncols)]
            self.row_num += 1
            return row
        else:
            raise StopIteration

    def next(self):
        return self.__next__()

class DictReader:
    def __init__(self, f, fieldnames=None, restkey=None, restval=None, sheet_index=0, *args, **kwds):
        self._fieldnames = fieldnames
        self.restkey = restkey
        self.reader = Reader(f, sheet_index, *args, **kwds) 
        self.row_num = self.reader.row_num

    def __iter__(self):
        return self

    @property
    def fieldnames(self):
        if self._fieldnames is None:
            try:
                self._fieldnames = next(self.reader)
            except StopIteration:
                pass
        self.row_num = self.reader.row_num
        return self._fieldnames
    
    @fieldnames.setter
    def fieldnames(self, value):
        self._fieldnames = value
        
    def __next__(self):
        if self.row_num == 0:
            self.fieldnames
        row = next(self.reader)
        self.row_num = self.reader.row_num
        
        # We prefer not to return blanks
        while row == []:
            row = next(self.reader)
        d = OrderedDict(zip(self.fieldnames, row))
        len_fieldnames = len(self.fieldnames)
        len_row = len(row)
        if len_fieldnames < len_row:
            d[self.restkey] = row[len_fieldnames:]
        elif len_fieldnames > len_row:
            for key in self.fieldnames[len_row:]:
                d[key] = self.restval
        return d

    def next(self):
        return self.__next__()
