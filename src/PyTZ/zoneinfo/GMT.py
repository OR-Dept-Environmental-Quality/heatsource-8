'''tzinfo timezone information for GMT.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class GMT(StaticTzInfo):
    '''GMT timezone definition. See datetime.tzinfo for details'''
    zone = 'GMT'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'GMT'

GMT = GMT()

