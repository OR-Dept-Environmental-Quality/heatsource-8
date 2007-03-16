'''tzinfo timezone information for Etc/GMT_minus_3.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class GMT_minus_3(StaticTzInfo):
    '''Etc/GMT_minus_3 timezone definition. See datetime.tzinfo for details'''
    zone = 'Etc/GMT_minus_3'
    _utcoffset = timedelta(seconds=10800)
    _tzname = 'GMT-3'

GMT_minus_3 = GMT_minus_3()

