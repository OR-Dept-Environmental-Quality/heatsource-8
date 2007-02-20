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
        elif isinstance(arg, list) or isinistance(arg,tuple):
            start = arg[0]
            stop = arg[1]
            step = arg[2] if len(arg) > 2 else None
            return slice(start,stop,step)
    def __getitem__(self,arg):
        col = slice(None,None,None)
        temp_sheet = None
        try:
            if len(arg) > 1: # We have a tuple or list
                row = self.__makeSlice(arg[0])
                col = self.__makeSlice(arg[1])
                if len(arg) >2: # we have a temporary sheet
                    temp_sheet = self.sheet
                    self.SetSheet(arg) # Error catching in the method
            else:
                row = self.__makeSlice(arg) # the slice can only be a row if there's only one element.
        except TypeError: # The slice() object has no __len__ attribute, so the if len(arg) will fail if it's a slice
            if isinstance(arg,slice):
                row = self.__makeSlice(arg)
            else: raise

        range1 = range2 = None
        # A few cases. We need to clean this syntax up.
        # First case, we have a rectangular range
        if row.start and col.start: range1 = self.excelize(col.start) + `row.start`
        if row.stop and col.stop: range2 = self.excelize(col.stop) + `row.stop`
        value = None
        if range1 and range2:
            try:
                value = self.GetValue("%s:%s"%(range1,range2))
            except: raise
        # Second case, we have a single number
        elif range2:
            try:
                value = self.GetValue(range2)
            except: raise
        # We don't have ranges, so we were only given a row to return.
        else:
            value = [] # make a list of rows
            cstart = self.excelize(0)
            cstop = self.excelize(255)
            for i in xrange(row.start, row.stop+1):
                # So we get the entire row and filter it removing blanks and putting them in a list
                # Appending that list to value. So value here is a list of lists.
                # Get the entire row- 256 columns is Excel's max, so we get it all, just in case.
                r = [i for i in self.GetValue("%s%i:%s%i" % (cstart, i, cstop, i))]
                r.reverse() # Reverse so we can remove all the Null items
                r = [i for i in dropwhile(lambda x: x==None, r)] # Remove all the empty (None) items
                r.reverse() # Reverse back to original
                value.append(tuple(r)) # Append this list
            value = value[0] if len(value) == 1 else value
        if temp_sheet: self.SetSheet(temp_sheet) #Clear the sheet value
        return value

    def ClearCalcData(self):
        if len(self.calcDataRange) == 0: return
