from unittest import TestCase
from Utils.EightFoldPath import EightFoldPath

class TestEightFoldPath(TestCase):
    def setUp(self):
        #                          N NE  E SE  S SW  W NW
        self.path = EightFoldPath([1, 2, 3, 4, 5, 6, 7, 8])
    def tearDown(self): pass

    def test_basic(self):
        "Test basic Get/Set and properties"
        self.assertEqual(self.path.S, 5)
        self.path.NW = 100
        self.path.SE = 50
        self.assertEqual(self.path.paths["NW"],100)
        self.assertNotEquals(self.path.GetSE(), 4)
    def test_iter(self):
        "test iteration"
        self.path.NW = 100
        self.path.SE = 50
        count = 0
        n = 0
        for k in self.path:
            assert isinstance(k,str)
            count += 1
        for k in self.path.iterkeys():
            assert isinstance(k,str)
            count += 1
        for v in self.path.itervalues():
            assert isinstance(v,int)
            count += 1
        for k,v in self.path.iteritems():
            assert isinstance(k,str)
            assert isinstance(v,int)
            n += v
            count += 1

        self.assertEquals(count, 8*4)
        self.assertEquals(n, 1+2+3+50+5+6+7+100)