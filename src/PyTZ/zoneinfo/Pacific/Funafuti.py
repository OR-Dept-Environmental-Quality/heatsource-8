'''tzinfo timezone information for Pacific/Funafuti.'''
from PyTZ.tzinfo import StaticTzInfo
from PyTZ.tzinfo import memorized_timedelta as timedelta

class Funafuti(StaticTzInfo):
    '''Pacific/Funafuti timezone definition. See datetime.tzinfo for details'''
    zone = 'Pacific/Funafuti'
    _utcoffset = timedelta(seconds=43200)
    _tzname = 'TVT'

Funafuti = Funafuti()

