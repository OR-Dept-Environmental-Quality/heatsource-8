'''tzinfo timezone information for Pacific/Tarawa.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Tarawa(StaticTzInfo):
    '''Pacific/Tarawa timezone definition. See datetime.tzinfo for details'''
    zone = 'Pacific/Tarawa'
    _utcoffset = timedelta(seconds=43200)
    _tzname = 'GILT'

Tarawa = Tarawa()

