'''tzinfo timezone information for Etc/UCT.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class UCT(StaticTzInfo):
    '''Etc/UCT timezone definition. See datetime.tzinfo for details'''
    zone = 'Etc/UCT'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'UCT'

UCT = UCT()

