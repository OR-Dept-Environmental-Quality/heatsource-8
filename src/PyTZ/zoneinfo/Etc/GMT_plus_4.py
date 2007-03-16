'''tzinfo timezone information for Etc/GMT_plus_4.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class GMT_plus_4(StaticTzInfo):
    '''Etc/GMT_plus_4 timezone definition. See datetime.tzinfo for details'''
    zone = 'Etc/GMT_plus_4'
    _utcoffset = timedelta(seconds=-14400)
    _tzname = 'GMT+4'

GMT_plus_4 = GMT_plus_4()

