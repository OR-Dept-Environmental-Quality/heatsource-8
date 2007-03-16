'''tzinfo timezone information for Africa/Bujumbura.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Bujumbura(StaticTzInfo):
    '''Africa/Bujumbura timezone definition. See datetime.tzinfo for details'''
    zone = 'Africa/Bujumbura'
    _utcoffset = timedelta(seconds=7200)
    _tzname = 'CAT'

Bujumbura = Bujumbura()

