'''tzinfo timezone information for Etc/Zulu.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Zulu(StaticTzInfo):
    '''Etc/Zulu timezone definition. See datetime.tzinfo for details'''
    zone = 'Etc/Zulu'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'UTC'

Zulu = Zulu()

