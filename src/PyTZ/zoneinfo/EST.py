'''tzinfo timezone information for EST.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class EST(StaticTzInfo):
    '''EST timezone definition. See datetime.tzinfo for details'''
    zone = 'EST'
    _utcoffset = timedelta(seconds=-18000)
    _tzname = 'EST'

EST = EST()

