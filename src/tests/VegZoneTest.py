from unittest import TestCase
from Utils.VegZone import VegZone

class TestVegZone(TestCase):
    def setUp(self): pass
    def tearDown(self): pass
    def testAccess(self):
        """Test access methods for VegZone"""
        v1 = VegZone(23,43,VDensity=4)
        v2 = VegZone(23,43,Overhang=4)

        self.assertEqual(v1['Elevation'],v1.Elevation)
        self.assertEqual(v1[0],v1.Elevation)
        self.assertEqual(v1.Elevation,23)
        self.assertEqual(v1[0],v2[0])
        self.assertNotEqual(v1[0:4],v2[0:4])
        self.assertEqual(v1[0:2],v2[0:2])
        self.assertEqual(v1.Overhang, v2.VDensity)
        self.assertEqual(v1.Overhang, None)
        self.assertRaises(AttributeError,getattr,v1,'test')
        self.assertRaises(AttributeError,setattr,v1,'test',3)
        v1.Overhang = 15
        v2["VDensity"] = 15
        self.assertEqual(v1[3],v2[2])
        v1[0] = 34
        self.assertNotEqual(v1.Elevation,v2.Elevation)
        v1.SlopeHeight = 3
        self.assertEqual(v1.SlopeHeight, 3)


