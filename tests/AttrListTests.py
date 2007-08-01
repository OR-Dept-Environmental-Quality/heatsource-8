from __future__ import division
import random
from unittest import TestCase
from Containers.DataPoint import DataPoint
from Containers.AttrList import AttrList, TimeList, PlaceList
from bisect import bisect_left, bisect_right

class TestAttrList(TestCase):
    def setUp(self):
        self.TL = TimeList()
        self.PL = PlaceList()
        for t in xrange(random.randint(30,100)):
            u = random.randint(1,30)
            v = random.random()+random.randint(1,30)
            self.TL.append(DataPoint(v,time=t+u))
        for p in xrange(random.randint(30,100)):
            u = random.randint(1,30)
            v = random.random()+random.randint(1,30)
            self.PL.append(DataPoint(v,place=p+u))


    def test_TimeList(self):
        for i in xrange(1,len(self.TL[:-1])):
            self.assertTrue(self.TL[i].t >= self.TL[i-1].t)


        for i in xrange(1,len(self.PL[:-1])):
            self.assertTrue(self.PL[i].x >= self.PL[i-1].x)

        L = self.PL.vsort()
        for i in xrange(1,len(L[:-1])):
            self.assertTrue(L[i],L[i-1])

    def test_GetItem(self):
        v = self.TL[3]
        x = self.TL[3:5]
        w = self.TL[4,1]
        y = self.TL[:3,None]
#        z = self.TL[20:40,1]
#        self.assertTrue(isinstance(z,list))
        self.assertTrue(isinstance(v,float))
        self.assertTrue(isinstance(w,float))
#        self.assertTrue(isinstance(z,list))
        self.assertTrue(isinstance(y,list))
        for lst in [x,y]:
            for i in lst:
                self.assertTrue(isinstance(i,float))
    def test_ComplexGetItem(self):
        PL = PlaceList(orderdn=True)
        TL = TimeList()
        # Values going into the lists
        pval = [52.0, 62.0, 39.0, 54.0, 9.0, 45.0, 91.0, 78.0, 78.0, 68.0, 96.0, 5.0, 61.0, 72.0]
        tval = [38.0, 29.0, 23.0, 49.0, 2.0, 32.0, 62.0, 82.0, 38.0, 61.0, 92.0, 100.0, 66.0, 1.0]
        pattr = [50, 88, 97, 75, 13, 94, 79, 17, 78, 5, 89, 85, 52, 76]
        tattr = [73, 76, 98, 4, 43, 92, 53, 67, 87, 47, 22, 9, 56, 10]

        for i in xrange(14):
            PL.append(DataPoint(pval[i],place=pattr[i]))
            TL.append(DataPoint(tval[i],time=tattr[i]))
        self.assertRaises(IndexError, PL.__getitem__,(87,0))

        self.assertEqual(PL[87,1],5.0)
        self.assertEqual(PL[87,-1],62.0)
        self.assertEqual(TL[23,1],2.0)
        self.assertEqual(TL[23,-1],92.0)
        self.assertEqual(PL[88,0],62.0)
        self.assertEqual(TL[22,0],92.0)

        # values after internal sorting
        pval_ordered =  [39.0, 45.0,  96.0, 62.0, 5.0, 91.0, 78.0, 72.0, 54.0, 61.0, 52.0, 78.0, 9.0,  68.0]
        tval_ordered =  [49.0, 100.0, 1.0,  92.0, 2.0, 61.0, 62.0, 66.0, 82.0, 38.0, 29.0, 38.0, 32.0, 23.0]
        pattr_ordered = [97,   94,    89,   88,   85,  79,   78,   76,   75,   52,   50,   17,   13,   5]
        tattr_ordered = [4,    9,     10,   22,   43,  47,   53,   56,   67,   73,   76,   87,   92,   98]

        pval.reverse() # values get reversed when ordering down
        for i in xrange(14):
            self.assertEqual(PL[i], pval_ordered[i]) # value check
            self.assertEqual(PL[i].x, pattr_ordered[i]) # attr check
            self.assertEqual(TL[i], tval_ordered[i]) # value check
            self.assertEqual(TL[i].t, tattr_ordered[i]) # attr check

        # Normal slicing was tested above, test our complex slicing here.

        print ""
        self.assertEqual(PL[3:50,None],PL[3:50]) # Should be normal slice

        # There is no object with an attribute of 38. Next down is 17, next up is 50
        self.assertEqual(PL[38,1],78)
        self.assertEqual(PL[38,1].x,17)
        self.assertEqual(PL[38,-1],52)
        self.assertEqual(PL[38,-1].x,50)
        self.assertRaises(IndexError, PL.__getitem__,(38,0))

        # There is no object with an attribute of 18. Next down is 22, next up is 10
        self.assertEqual(TL[18,1],92)
        self.assertEqual(TL[18,1].t,22)
        self.assertEqual(TL[18,-1],1)
        self.assertEqual(TL[18,-1].t,10)
        self.assertRaises(IndexError, TL.__getitem__,(18,0))

        self.assertEqual(PL[78,0],78)
        self.assertEqual(PL[78,0].x,78)
        self.assertEqual(PL[78,0],PL[6])

        # Should order equivalantly
#        self.assertEqual(PL[95:3, -1], PL[3:95, -1])
#        self.assertEqual(TL[11:68, 1], TL[68:11,1])
#        self.assertEqual(TL[23:46,0], TL[23:46,0])


#        self.assertEqual(PL[15:93, -1],pval_ordered[1:-2])
#        self.assertEqual(map(lambda x: x.x,PL[15:93, -1]), pattr_ordered[1:-2])
#        self.assertEqual(PL[15:93, 1], pval_ordered[2:-2])
#        self.assertEqual(map(lambda x: x.x, PL[15:93, 1]), pattr_ordered[2:-2])

#        self.assertEqual(PL[15:93, -1],pval_ordered[1:-2])
#        self.assertEqual(map(lambda x: x.x,PL[15:93, -1]), pattr_ordered[1:-2])
#        self.assertEqual(PL[15:93, 1], pval_ordered[2:-2])
#        self.assertEqual(map(lambda x: x.x, PL[15:93, 1]), pattr_ordered[2:-2])

