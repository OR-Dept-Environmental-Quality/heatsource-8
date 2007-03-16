'''tzinfo timezone information for Etc/Greenwich.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Greenwich(StaticTzInfo):
    '''Etc/Greenwich timezone definition. See datetime.tzinfo for details'''
    zone = 'Etc/Greenwich'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'GMT'

Greenwich = Greenwich()

