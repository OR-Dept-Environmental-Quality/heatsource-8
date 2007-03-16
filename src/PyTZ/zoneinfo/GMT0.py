'''tzinfo timezone information for GMT0.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class GMT0(StaticTzInfo):
    '''GMT0 timezone definition. See datetime.tzinfo for details'''
    zone = 'GMT0'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'GMT'

GMT0 = GMT0()

