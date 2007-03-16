'''tzinfo timezone information for Etc/UTC.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class UTC(StaticTzInfo):
    '''Etc/UTC timezone definition. See datetime.tzinfo for details'''
    zone = 'Etc/UTC'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'UTC'

UTC = UTC()

