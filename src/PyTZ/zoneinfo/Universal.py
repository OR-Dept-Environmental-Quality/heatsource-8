'''tzinfo timezone information for Universal.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Universal(StaticTzInfo):
    '''Universal timezone definition. See datetime.tzinfo for details'''
    zone = 'Universal'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'UTC'

Universal = Universal()

