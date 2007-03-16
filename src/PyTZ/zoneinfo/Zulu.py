'''tzinfo timezone information for Zulu.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Zulu(StaticTzInfo):
    '''Zulu timezone definition. See datetime.tzinfo for details'''
    zone = 'Zulu'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'UTC'

Zulu = Zulu()

