'''tzinfo timezone information for Etc/Universal.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Universal(StaticTzInfo):
    '''Etc/Universal timezone definition. See datetime.tzinfo for details'''
    zone = 'Etc/Universal'
    _utcoffset = timedelta(seconds=0)
    _tzname = 'UTC'

Universal = Universal()

