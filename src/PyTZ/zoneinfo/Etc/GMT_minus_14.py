'''tzinfo timezone information for Etc/GMT_minus_14.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class GMT_minus_14(StaticTzInfo):
    '''Etc/GMT_minus_14 timezone definition. See datetime.tzinfo for details'''
    zone = 'Etc/GMT_minus_14'
    _utcoffset = timedelta(seconds=50400)
    _tzname = 'GMT-14'

GMT_minus_14 = GMT_minus_14()

