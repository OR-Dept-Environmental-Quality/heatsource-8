'''tzinfo timezone information for Pacific/Wake.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Wake(StaticTzInfo):
    '''Pacific/Wake timezone definition. See datetime.tzinfo for details'''
    zone = 'Pacific/Wake'
    _utcoffset = timedelta(seconds=43200)
    _tzname = 'WAKT'

Wake = Wake()

