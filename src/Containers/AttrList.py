from __future__ import division
from DataPoint import DataPoint
from datetime import datetime
from itertools import ifilter

# TODO: Implement a matrix for datapoint containers that need both time and place.

class AttrList(list):
    """General container that is organized, and indexed, via attribute

    This class defines a list container for any type. The list is
    ordered by 'attr', either ascending or descending ('orderdn'), and
    can be indexed by the attribute or by normal slicing. Subclasses
    might override the __getitem__ and __setitem__ methods to ensure
    proper attribute access. The class uses a sort key self.cmp which can
    be a function taking a single argument or a lambda construct.

    Indexing and slicing is done by the named attribute when the object is
    indexed with an optional parameter. Thus, we can return objects either
    by normal list index (placement)

    >>> from random import randint
    >>> class MeterObject(object):
    >>>     def __init__(self, meter):
    >>>         self.meter = meter
    >>>     def __repr__(self): return "Meter: %i"%self.meter
    >>> lst = AttrList(attr='meter')
    >>> for i in xrange(10):
    >>>     lst.append(MeterObject(randint(4,30)) #Automagically sorts by meter after each append
    >>> print lst[0]
    Meter: 5
    >>> print lst[1:3]
    [Meter: 6, Meter: 12]
    >>>

    Or we can index/slice them by the attribute. When accessing by attribute,
    we send the index or slice, and a second argument which is either a 1, -1, or 0.
    This argument tells us whether to return elements by 'looking' forward,
    backward or straight ahead respectively. Straight ahead raises an IndexError
    if there is not an object with an attribute equal to the given index.

    For instance, we may be defining a stream reach, and want to know, at an
    arbitrary stream meter, what is the upstream node that is affecting us. For
    this, we would want to look upstream. Thus, assuming that AttrList was
    defined with orderdn=True (streams are measured from the mouth up, but flow
    down) we would be looking backwards (upstream).

    >>> lst = AttrList(attr='meter', orderdn=True) # Make list in descending order
    ...
    >>> print lst[6] #7th element in sequence
    Meter: 22
    >>> print lst[7] #8th element in sequence
    Meter: 20
    >>> print lst[20,0] # directly access first element with meter=20
    Meter: 20
    >>> print lst[21,-1] # Access element with meter=21, looking backward
    Meter: 22
    >>> print lst[21, 1] # access element with meter=21, looking forward
    Meter: 20
    >>> print lst[21,0] # access element with meter=21, looking straight ahead
    IndexError...
    >>>

    Slicing works in a similiar fashion. Slicing still works like Pythonically,
    thus it returns in (min,max] fashion. Furthermore, the slicing automagically
    converts to the correct order, depending on whether we are ordered up or down.
    Thus, returning a slice of lst[20:30,-1] on a descending ordered list, starts
    the slice at meter 30 and ends at 20. When slicing while looking straight ahead,
    an IndexError is not raised if there is no object with an attribute equal to the
    stopping point, because we are going to, but not including, that stopping point.
    An IndexError is likewise not raised when there is not attribute equal to the
    starting point because there is an implicit assumption that we will start at
    the object with that value, or the next INNER object with that value. In other
    words, we will start on the value, or at the next value inbetween that value and
    the starting point. Thus, slicing while looking forwards and looking straight
    ahead are always? equivalent.

    >>> print lst[5]
    Meter: 23
    >>> print lst[4]
    Meter: 30
    >>> print lst[3]
    Meter: 31
    >>> print lst[3:7]
    [Meter: 30, Meter: 23, Meter: 22, Meter: 20]
    >>> print lst[20:30,-1]
    [Meter: 30, Meter:23, Meter: 22]
    >>> print lst[20:30,1]
    [Meter: 30, Meter:23, Meter: 22]
    >>> print lst[21:30, 0]  # Doesn't raise IndexError because we are stoping before 21 anyway
    [Meter: 30, Meter:23, Meter: 22]
    >>> print lst[29:20, -1]
    [Meter: 30, Meter: 23, Meter: 22]
    >>> print lst[29:20, 1]
    [Meter: 23, Meter: 22]
    >>> print lst[29:20, 0] # Doesn't raise IndexError because it starts at next INNER node
    [Meter: 23, Meter: 22]
    >>>

    Because a sort key is used, the type of object included in the list is not
    enforced. This is a potential problem because the sort can fail if there
    is an object included that cannot supply the method necessary for the
    comparison key. However, I chose to keep this uninforced to allow Pythonic
    inclusion in this list of anything that acts, walks or quacks like the
    appropriate duck.
    """
    def __init__(self, val=[], attr=None, orderdn=False):
        list.__init__(self, val)

        self.attr = attr
        self.orderdn = orderdn
        # lambda to return the named attribute
        self.key = lambda x: getattr(x, attr)
    def sort(self):
        """Sort our contents by the desired attribute and direction, setting references to prev/next items

        This is a one-directional sort, and since DataPoints can hold two orthogonal indices, multi-sorting
        is not implemented here. Individual subclasses of AttrList must override this method if sorting
        is required on both the x (place) and t (time) axes"""
        if not self.key:
            raise Exception("Subclasses of AttrList must implement a comparison key in self.cmp")
        # Sort ourselves using the internal comparison key
        super(AttrList,self).sort(key=self.key,reverse=self.orderdn)
        # Then set the next and previous node references according to the new sort. This is an optional
        # utility because attr can be none. However, if attr is set, then each node within the list will
        # have attributes called 'prev_<attr>' and 'next_<attr>' set as references to the previous and
        # next instances in the list, where <attr> is the string supplied in the attr keyword argument.
        if self.attr:
            for i in xrange(len(self)):
                this = self[i]
                prev = self[i-1] if i else None # Only set if i > 0, otherwise i-1 equals the LAST node.
                try: next = self[i+1]
                except IndexError: next = None
                # Use self.attr to build an attribute string to set the next and previous attributes
                # using the setattr() function
                p_attr = 'prev_%s' % self.attr
                n_attr = 'next_%s' % self.attr
                setattr(this, p_attr, prev)
                setattr(this, n_attr, next)
    def vsort(self, rev=False):
        """Return a copy of self, sorted by value, rather than by attribute

        This protects the self's representation from being sorted by value, which
        would screw-up our intention of keep us sorted by attribute, but allows us
        access to a list sorted by value if we want it."""
        return sorted(self, reverse=rev)
    def __index__(self, ind): return super(self.type,self).__index__(ind)
    def __iadd__(self, object): self.append(object)
    def append(self, object):
        super(AttrList,self).append(object)
        self.sort()
    def __setitem__(self, *args):
        super(AttrList, self).__setitem__(*args)
        self.sort()
    def __getitem__(self,args):
        # If we are given a slice or an integer, we return the list bounds.
        if isinstance(args,int) or isinstance(args,slice):
            return super(AttrList, self).__getitem__(args)
        # If we are given a tuple, then the first item should be an integer, float or slice,
        # and the second item should be true or false, saying whether we want to
        # index by attribute or not (true or false)
        look = args[1]
        index = args[0]
        if index is None: raise IndexError("Cannot index %s with None."%self.__class__.__name__)

        if look is None: return super(AttrList,self).__getitem__(args[0]) # index by value
        if not self.attr: #the attr keyword is optional, make sure we have it defined
            raise Exception("Indexing by attribute is only possible when %s is constructed with an 'attr' keyword value" % self.__class__.__name__)
        # We are not a slice, so we return the indexed value

        # This is the value of x and is used for convenience in the test functions below
        v = lambda x:getattr(x, self.attr)


        if not isinstance(index, slice):
            # define a test function based on which way we are looking
            if look == 0: # get only if an attribute is equal
                test = lambda x: v(x) == index
            elif (look == 1 and self.orderdn) or (look == -1 and not self.orderdn): # We are looking for the next smaller value
                test = lambda x:v(x) <= index
            elif (look == 1 and not self.orderdn) or (look == -1 and self.orderdn): # We are looking for the next larger value
                test = lambda x:v(x) >= index
            else:
                raise Exception("Problem in the attribute slicing. Exception called for traceback")
            # Now, we have a test which returns true if the value is appropriate. We use the
            # "vectorized" version of a search in takewhile, but we only return the first value
            # from the iterator.
            try:
                # ifilter() runs the test on self and returns all the values that
                # test positive.
                # If we are looking backward, we need to grab from the end of the list.
                # otherwise, we grab from the front.
                ind = -1 if look == -1 else 0
                return list(ifilter(test,self))[ind]
            except IndexError:
                raise IndexError("No value possible for attribute %s: %s." %(self.attr, index))


        else: # We are working with a slice, so we need to do a bit more work.
            # First, get a minimum and maximum value to work with, since a slice can have None
            # for these and go to beginning or end.
            l = map(lambda x:getattr(x,self.attr),self)
            min = index.start or min(l)
            max = index.stop or max(l)
            if min > max: min,max = max,min
            # Now, if we are ordered descending, these are switched.
            # Define a test function an create a list of included values
            l = list(ifilter(lambda x: v(x) >= min and v(x) < max,self))
            # Now we define our test function.
            if look == 0 or look == 1: # Normal slice, next INNER object if v(x) != min
                return l # the list is good enough in this case
            else: # Here we have to do some magic, because we have to find the next larger or smaller object.
                if v(l[0]) == min: return l # the lowest attribute is exact. Return.
                i = self.index(l[0]) # Otherwise, get the list index from self of the lowest value in the temporary list.
                if not i: return l # if that index is zero, then we've grabbed the list from the start, so return.
                l.insert(0, self[i-1]) # otherwise, insert this object at the beginning
                return l # then return the list.

class TimeList(AttrList):
    """list class that can be indexed by slice or by time

    This class is useful for any continuous data so that data can be accessed
    by the list slice or by the time of occurrance, since the list is organized
    by the timefield.
    """
    def __init__(self, val=[], attr='t', orderdn=False):
        AttrList.__init__(self, val, attr, orderdn=orderdn)

class PlaceList(AttrList):
    """AttrList subclass with place as a the index key

    This class sorts in descending order by default, because it is mostly used
    for StreamNode storage
    """
    def __init__(self, val=[], attr='x', orderdn=False):
        AttrList.__init__(self, val, attr, orderdn=orderdn)
