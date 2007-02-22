from unittest import TestCase
from Excel.ExcelDocument import ExcelDocument

class TestExcelDocument(TestCase):
    def setUp(self):
        self.doc = ExcelDocument()
        self.doc1 = ExcelDocument()
    def tearDown(self):
        self.doc.Close()
        self.doc1.Close()
        self.doc.Quit()
        self.doc1.Quit()
    def test_basic(self):
        """Test new, open, close, etc."""
        self.doc.New()
        self.doc.SetValue("A1","testing")
        self.doc.SetValue("A2",3.01)
        self.doc.SetValue("A3","1/31/2007")

        self.assertEqual(self.doc.GetValue("a2"),3.01)
        self.doc.SaveAs("C:\\temp\\test.xls")
        self.doc1.Open("C:\\temp\\test.xls")
        self.assertEqual(self.doc1.GetValue("a2"),3.01)
        self.assertEqual(self.doc1.GetValue("a1"),"testing")
    def test_sheet(self):
        self.doc.SetSheet(2)
    def test_range(self):
        rng = [range(100) for i in range(26)]
        self.doc.New()
        self.doc.SetValue("a1:z100",rng)
        self.assertEqual(self.doc.GetValue("c3",'Sheet1'),2.0)
        self.assertEqual(self.doc.GetValue((4,3),'Sheet1'),3.0)
        l = ((0.0, 1.0, 2.0, 3.0, 4.0), (0.0, 1.0, 2.0, 3.0, 4.0), (0.0, 1.0, 2.0, 3.0, 4.0))
        self.assertEqual(self.doc.GetValue("A2:e4",'Sheet1'), l)
        # In the infinite Micro$oft wisdom, Excel uses column first
        # when accessing as 'A1' but it uses row first when accessing as
        # (1,0). Idiots.
        self.assertEqual(self.doc.GetValue((1,0,3,4),'Sheet1'),l)
        self.assertEqual(self.doc.GetValue(((1,0),(3,4)),'Sheet1'),l)


    def test_excelize(self):
        self.assertEqual(self.doc.excelize(0),"A")
        self.assertEqual(self.doc.excelize(18),"S")
        self.assertEqual(self.doc.excelize(25),"Z")
        self.assertEqual(self.doc.excelize(26),"AA")
        self.assertEqual(self.doc.excelize(40),"AO")
        self.assertEqual(self.doc.excelize(51),"AZ")
        self.assertEqual(self.doc.excelize(99),"CV")
    def test_deExcelize(self):
        self.assertEqual(self.doc.deExcelize("A"),0)
        self.assertEqual(self.doc.deExcelize("S"),18)
        self.assertEqual(self.doc.deExcelize("Z"),25)
        self.assertEqual(self.doc.deExcelize("AA"),26)
        self.assertEqual(self.doc.deExcelize("AO"),40)
        self.assertEqual(self.doc.deExcelize("AZ"),51)
        self.assertEqual(self.doc.deExcelize("CV"),99)
