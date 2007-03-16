'''tzinfo timezone information for Pacific/Yap.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Yap(StaticTzInfo):
    '''Pacific/Yap timezone definition. See datetime.tzinfo for details'''
    zone = 'Pacific/Yap'
    _utcoffset = timedelta(seconds=36000)
    _tzname = 'TRUT'

Yap = Yap()

