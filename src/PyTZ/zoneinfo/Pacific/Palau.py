'''tzinfo timezone information for Pacific/Palau.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Palau(StaticTzInfo):
    '''Pacific/Palau timezone definition. See datetime.tzinfo for details'''
    zone = 'Pacific/Palau'
    _utcoffset = timedelta(seconds=32400)
    _tzname = 'PWT'

Palau = Palau()

