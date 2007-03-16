'''tzinfo timezone information for UCT.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class UCT(StaticTzInfo):
    '''UCT timezone definition. See datetime.tzinfo for details'''
    zone = 'UCT'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'UCT'

UCT = UCT()

