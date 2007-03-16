'''tzinfo timezone information for MST.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class MST(StaticTzInfo):
    '''MST timezone definition. See datetime.tzinfo for details'''
    zone = 'MST'
    _utcoffset = timedelta(seconds=-25200)
    _tzname = 'MST'

MST = MST()

