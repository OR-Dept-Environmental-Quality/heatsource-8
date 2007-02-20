from unittest import TestCase
from random import randint
from Excel.DataSheet import DataSheet
class TestDataSheet(TestCase):
    def setUp(self):
        self.doc = DataSheet()
        self.doc.New()
        # Use the ExcelDocument method to set the value
        for col in range(10):
            for row in range(10):
                self.doc.SetValue("%s%i"%(chr(col+65),row+1), (row + 1)*col )
        def check(start,stop):
            if start > stop: start, stop == stop, start
            if start == stop: stop += 5
            return start,stop
        self.rstart,self.rstop = check(randint(0,10),randint(0,100))
        self.cstart,self.cstop = check(randint(0,10),randint(0,10))

    def tearDown(self):
        self.doc.Quit()
    def testSlice(self):
        """Test the slicing and __getitem__ functionality"""
        r1 = 2
        c1 = 2
        r2 = 8
        c2 = 8

        #individual cells
        self.assertEqual(self.doc[r1,c1], r1 *c1 )
#        self.assertEqual(len(self.doc),10)
        self.assertEqual(len(self.doc[r1:r2]),7)
        rng = self.doc[r1:r2,c1:c2]
        for i in xrange(len(rng)):
            row = rng[i]
            self.assertEqual(len(row),7)
            for j in xrange(len(row)):
                col = row[j]
                # We need to add the offset because we don't grab starting at the beginning.
                # Thus, what would be i*j becomes (i+r1)*(j+c1)
                self.assertEqual(col,(i+r1)*(j+c1))
        self.doc.Close()
    def testOpening(self):
        """Test ability to open a file and read from it"""
        self.doc.Close()
        self.doc.Quit()
        doc = DataSheet(filename="c:\\eclipse\\HeatSource\\Toketee_CCC.xls")
        


