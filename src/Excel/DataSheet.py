from itertools import dropwhile
import datetime
from ExcelDocument import ExcelDocument

class DataSheet(ExcelDocument):
    """Class defining one single sheet of data within the greater Excel document

    This class is something of an abstraction layer because we may eventually move
    away from an Excel interface, but this class may still serve to link the back
    end to the front-end, which may be wxPython, datafiles, SQL, Excel, etc."""
    def __init__(self, filename=None, show=False):
        ExcelDocument.__init__(self,show)
        if filename:
            self.Open(filename)
        # Data that the user enters into the spreadsheet (i.e. via TTools)
        self.userDataRange = []
        # Data that's calculated and added to the sheet
        self.calcDataRange = []

    def __makeSlice(self, arg):
        if isinstance(arg,int): return slice(None,arg,None)
        elif isinstance(arg, slice): return arg
        elif isinstance(arg, list) or isinstance(arg,tuple):
            start = arg[0]
            stop = arg[1]
            step = arg[2] if len(arg) > 2 else None
            return slice(start,stop,step)
    def __getitem__(self,arg):
        col = slice(None,None,None)
        sheet = self.sheet
        try:
            if len(arg) > 1: # We have a tuple or list
                row = self.__makeSlice(arg[0])
                col = self.__makeSlice(arg[1])
                if len(arg) >2: # we have a temporary sheet
                    sheet = arg[2]
            else:
                row = self.__makeSlice(arg) # the slice can only be a row if there's only one element.
        except TypeError: # The slice() object has no __len__ attribute, so the 'if len(arg)' will fail if it's a slice
            if isinstance(arg,slice):
                row = self.__makeSlice(arg)
            else: raise

        blank = slice(None,None,None)
        cstart, cstop = 0,255 # Default Excel column bounds
        rstart, rstop = 1,65536 # Default row bounds

        if (row and row != blank) and (col and col != blank): # we have values for both rows and columns
            # They should both have stop values, but we test anyway to make sure there's no funkiness
            if not row.stop: raise Exception("Row needs a stopping point")
            if not col.stop: raise Exception("Column needs a stopping point")
            #Then we make sure that both row and column have a starting point, which can be None coming in.
            # Here, we set it to the stopping point if it's None.
            rstart = row.start if row.start else row.stop
            rstop = row.stop
            cstart = col.start if col.start else col.stop
            cstop = col.stop
        elif not col or col == blank: # We want a full row or rows
            if not row or row == blank: raise Exception("Must choose row(s) and/or column(s) to get data")
            rstart = row.start if row.start else row.stop
            rstop = row.stop
        elif not row or row == blank: # We want a full column or columns,
            if not col or col == blank: raise Exception("Must choose row(s) and/or column(s) to get data")
            cstart = col.start if col.start else col.stop
            cstop = col.stop
        else: raise Exception("Logical error in %s" % self.__class__.__name__)

        # Now we have start and stop points for both rows and columns, so we just get the range
        range1 = self.excelize(cstart) + `rstart`
        range2 = self.excelize(cstop) + `rstop`
        value = self.GetValue("%s:%s"%(range1,range2),sheet=sheet)

        # If we are not a tuple of data from a range
        if not isinstance(value,tuple):
            return value
        # Otherwise, build a list for processing
        else: value = [i for i in value]

        # Having gotten the range, we may have overshot our available data. For instance, we may have
        # Chosen rows 1-5 when only 1-3 have data, or similar with columns. The resulting forms are:
        # For rows:
        # ( (0, 0, 0, None, None), (0, 0, 0, None, None), (0, 0, 0, None, None), ... )

        # For columns:
        # ( (0, 0), (0, 0), (0, 0), (None, None), (None, None), (None, None), ... )

        # What we want to do is cycle through the value matrix and remove all None values that are
        # at the END of a row or column (None values in the middle are important to keep)

        for i in xrange(len(value)):
            row = [j for j in value[i]]
            row.reverse()
            row = [k for k in dropwhile(lambda x:x==None, row)] # Drop all the null values at the end.
            row.reverse()
            value[i] = row
        value.reverse()
        value = [tuple(i) for i in dropwhile(lambda x: len(x) == 0, value)] # Drop the empty lists
        value.reverse()

        return tuple(value) # Keep everything as a tuple of tuples, as GetValue returns.

    def ClearCalcData(self):
        if len(self.calcDataRange) == 0: return
