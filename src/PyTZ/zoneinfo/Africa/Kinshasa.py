'''tzinfo timezone information for Africa/Kinshasa.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Kinshasa(StaticTzInfo):
    '''Africa/Kinshasa timezone definition. See datetime.tzinfo for details'''
    zone = 'Africa/Kinshasa'
    _utcoffset = timedelta(seconds=3600)
    _tzname = 'WAT'

Kinshasa = Kinshasa()

