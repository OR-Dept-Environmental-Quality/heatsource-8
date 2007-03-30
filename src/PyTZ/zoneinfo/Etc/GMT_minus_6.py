'''tzinfo timezone information for Etc/GMT_minus_6.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class GMT_minus_6(StaticTzInfo):
    '''Etc/GMT_minus_6 timezone definition. See datetime.tzinfo for details'''
    zone = 'Etc/GMT_minus_6'
    _utcoffset = timedelta(seconds=21600)
    _tzname = 'GMT-6'

GMT_minus_6 = GMT_minus_6()
